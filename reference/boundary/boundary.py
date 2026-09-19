"""
Gate III, enforced.

A catalog-driven tool boundary. Every argument of every tool has a pen:
application, model, or human. The boundary reads ``tools/catalog.yaml`` and
``config.yaml`` from an agent folder, and it is the only thing allowed to
execute a tool.

The model never imports this module. It proposes a tool call as a name and a
dict of arguments. The application hands that proposal to ``Boundary.call``.

    application pen  value comes from the session; a model-supplied value is ignored and logged
    model pen        validated by type, max_length, allowlist; rendered downstream, never executed
    human pen        refused without an Approval covering (tool, argument, value); escalates instead

Prompts request. Boundaries enforce.
"""
from __future__ import annotations

import dataclasses
import hashlib
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

import yaml

PENS = ("application", "model", "human")
TYPES = {"string": str, "integer": int, "number": (int, float), "boolean": bool}


class CatalogError(ValueError):
    """The catalog is malformed. Fail at load time, never at call time."""


@dataclass(frozen=True)
class Session:
    """What the application knows about this request. The source of every application-pen value."""

    user: str
    values: Mapping[str, Any] = field(default_factory=dict)
    allowlists: Mapping[str, Iterable[Any]] = field(default_factory=dict)

    def resolve(self, source: str) -> Any:
        prefix = "session."
        if not source.startswith(prefix):
            raise CatalogError(f"application-pen source must start with 'session.': {source!r}")
        key = source[len(prefix):]
        if key not in self.values:
            raise LookupError(f"session has no value for {key!r}")
        return self.values[key]


@dataclass(frozen=True)
class Approval:
    """A human's signature on one (tool, argument, value). Specific by design.

    Either ``value`` (exact match) or ``max_value`` (standing approval for any
    numeric value at or below it) must be given. ``expires_at`` is unix time.
    """

    tool: str
    arg: str
    approver: str
    value: Any = None
    max_value: float | None = None
    expires_at: float | None = None

    def covers(self, tool: str, arg: str, value: Any, now: float | None = None) -> bool:
        if (tool, arg) != (self.tool, self.arg):
            return False
        if self.expires_at is not None and (now if now is not None else time.time()) > self.expires_at:
            return False
        if self.max_value is not None:
            try:
                return float(value) <= self.max_value
            except (TypeError, ValueError):
                return False
        return value == self.value


@dataclass(frozen=True)
class Outcome:
    """What the boundary did with a proposal. ``kind`` is executed, escalated, rejected, or halted."""

    kind: str
    tool: str
    detail: str = ""
    arg: str | None = None
    value: Any = None
    result: Any = None
    record: dict | None = None

    @property
    def ok(self) -> bool:
        return self.kind == "executed"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class Boundary:
    """Loads an agent folder and enforces its catalog.

    ``tools`` maps tool name to the callable that actually does the work. Every
    registered tool must be in the catalog and every catalogued tool must be
    registered: a tool that is reachable but unlisted is model-writable by
    default, and the boundary refuses to start in that state.
    """

    def __init__(
        self,
        agent_dir: str | Path,
        tools: Mapping[str, Callable[..., Any]],
        audit: Callable[[dict], None] | None = None,
        clock: Callable[[], float] = time.time,
    ) -> None:
        self.agent_dir = Path(agent_dir)
        self.catalog_path = self.agent_dir / "tools" / "catalog.yaml"
        self.config_path = self.agent_dir / "config.yaml"
        self.catalog = self._load_catalog()
        self.catalog_hash = sha256_file(self.catalog_path)
        self.tools = dict(tools)
        self.audit = audit or (lambda record: None)
        self.clock = clock

        unlisted = set(self.tools) - set(self.catalog)
        if unlisted:
            raise CatalogError(f"tools reachable but not in catalog: {sorted(unlisted)}")
        unregistered = set(self.catalog) - set(self.tools)
        if unregistered:
            raise CatalogError(f"catalog lists tools that are not registered: {sorted(unregistered)}")

    # ------------------------------------------------------------------ loading

    def _load_catalog(self) -> dict[str, dict[str, dict]]:
        if not self.catalog_path.exists():
            raise CatalogError(f"no catalog at {self.catalog_path}")
        data = yaml.safe_load(self.catalog_path.read_text()) or {}
        tools = data.get("tools")
        if not isinstance(tools, dict) or not tools:
            raise CatalogError("catalog has no tools")
        for tool, args in tools.items():
            if not isinstance(args, dict) or not args:
                raise CatalogError(f"tool {tool!r} has no arguments listed")
            for arg, rule in args.items():
                if not isinstance(rule, dict) or rule.get("pen") not in PENS:
                    raise CatalogError(f"{tool}.{arg}: every argument needs a pen in {PENS}")
                if rule["pen"] == "application" and "source" not in rule:
                    raise CatalogError(f"{tool}.{arg}: application pen needs a 'source'")
                if rule.get("type") and rule["type"] not in TYPES:
                    raise CatalogError(f"{tool}.{arg}: unknown type {rule['type']!r}")
        return tools

    def config(self) -> dict:
        if not self.config_path.exists():
            return {}
        return yaml.safe_load(self.config_path.read_text()) or {}

    def kill_switch_on(self) -> bool:
        """Gate VI. Read on every call, so flipping the file stops the agent without a restart."""
        return bool(self.config().get("kill_switch", False))

    # ------------------------------------------------------------------ calling

    def call(
        self,
        name: str,
        model_args: Mapping[str, Any] | None,
        session: Session,
        approvals: Iterable[Approval] = (),
    ) -> Outcome:
        model_args = dict(model_args or {})
        approvals = list(approvals)
        notes: list[str] = []
        final: dict[str, Any] = {}

        def finish(outcome: Outcome) -> Outcome:
            record = {
                "ts": self.clock(),
                "tool": name,
                "kind": outcome.kind,
                "detail": outcome.detail,
                "actor": session.user,
                "risk_tier": self.config().get("risk_tier"),
                "catalog_hash": self.catalog_hash,
                "pens": {a: r["pen"] for a, r in self.catalog.get(name, {}).items()},
                "model_args": model_args,
                "final_args": final,
                "notes": notes,
            }
            self.audit(record)
            return dataclasses.replace(outcome, record=record)

        if self.kill_switch_on():
            return finish(Outcome("halted", name, "kill switch is on"))

        if name not in self.catalog:
            return finish(Outcome("rejected", name, "tool not in catalog"))
        spec = self.catalog[name]

        unknown = set(model_args) - set(spec)
        if unknown:
            return finish(Outcome("rejected", name, f"unknown arguments: {sorted(unknown)}"))

        for arg, rule in spec.items():
            pen = rule["pen"]

            if pen == "application":
                if arg in model_args:
                    notes.append(f"model attempted to write application-pen argument {arg!r}; ignored")
                try:
                    final[arg] = session.resolve(rule["source"])
                except LookupError as exc:
                    return finish(Outcome("rejected", name, str(exc), arg=arg))

            elif pen == "human":
                if arg not in model_args:
                    return finish(Outcome("rejected", name, f"human-pen argument {arg!r} missing", arg=arg))
                value = model_args[arg]
                if "allowed" in rule and value not in rule["allowed"]:
                    return finish(Outcome("rejected", name, f"{arg!r} value {value!r} not in allowed set", arg=arg, value=value))
                now = self.clock()
                if not any(a.covers(name, arg, value, now) for a in approvals):
                    return finish(Outcome("escalated", name, f"human-pen argument {arg!r} needs approval", arg=arg, value=value))
                final[arg] = value

            else:  # model pen
                ok, detail, value = self._validate(rule, arg, model_args.get(arg), session)
                if not ok:
                    return finish(Outcome("rejected", name, detail, arg=arg, value=model_args.get(arg)))
                final[arg] = value

        result = self.tools[name](**final)
        return finish(Outcome("executed", name, result=result))

    @staticmethod
    def _validate(rule: dict, arg: str, value: Any, session: Session) -> tuple[bool, str, Any]:
        if value is None:
            if rule.get("required", True):
                return False, f"model-pen argument {arg!r} missing", None
            return True, "", None
        t = rule.get("type")
        if t:
            expected = TYPES[t]
            if isinstance(value, bool) and t in ("integer", "number"):
                return False, f"{arg!r} must be {t}, got boolean", value
            if not isinstance(value, expected):
                return False, f"{arg!r} must be {t}, got {type(value).__name__}", value
        if "max_length" in rule and len(str(value)) > rule["max_length"]:
            return False, f"{arg!r} exceeds max_length {rule['max_length']}", value
        if "allowlist" in rule and value not in rule["allowlist"]:
            return False, f"{arg!r} value {value!r} not in allowlist", value
        if "allowlist_from" in rule:
            allowed = set(session.allowlists.get(rule["allowlist_from"], ()))
            if value not in allowed:
                return False, f"{arg!r} value {value!r} not in allowlist {rule['allowlist_from']!r}", value
        return True, "", value
