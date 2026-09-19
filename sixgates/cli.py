"""
sixgates: the Six Gates as a command.

    sixgates init  agents/expense-triage        scaffold an agent folder from the templates
    sixgates check agents/expense-triage        verify the ledger: gates signed, pens labelled, set frozen, owner named
    sixgates badge agents/expense-triage        write a README badge from config.yaml

`check` exits 0 when every gate passes, 1 when any gate fails. Warnings do not fail the run.
It reads only files. It never calls a model and never executes a tool.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = REPO_ROOT / "templates" / "agent"
PENS = {"application", "model", "human"}
GATES = [
    ("01-justify.md", "I", "Justify"),
    ("02-grade.md", "II", "Grade"),
    ("03-limit.md", "III", "Limit"),
    ("04-build.md", "IV", "Build"),
    ("05-prove.md", "V", "Prove"),
    ("06-run.md", "VI", "Run"),
]
PLACEHOLDER = re.compile(r"<[^>\n]{1,60}>")


# --------------------------------------------------------------------------- results

@dataclass
class Finding:
    level: str  # PASS | WARN | FAIL
    gate: str
    message: str


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)

    def add(self, level: str, gate: str, message: str) -> None:
        self.findings.append(Finding(level, gate, message))

    def ok(self, gate: str, message: str) -> None:
        self.add("PASS", gate, message)

    def warn(self, gate: str, message: str) -> None:
        self.add("WARN", gate, message)

    def fail(self, gate: str, message: str) -> None:
        self.add("FAIL", gate, message)

    @property
    def failed(self) -> bool:
        return any(f.level == "FAIL" for f in self.findings)

    def gate_status(self, gate: str) -> str:
        levels = {f.level for f in self.findings if f.gate == gate}
        if "FAIL" in levels:
            return "FAIL"
        if "WARN" in levels:
            return "WARN"
        return "PASS"


# --------------------------------------------------------------------------- helpers

def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text()) or {}


def signed(text: str) -> bool:
    """A gate is signed when it has a Signed: line with no placeholder left in it."""
    for line in text.splitlines():
        if line.strip().lower().startswith("signed"):
            return not PLACEHOLDER.search(line)
    return False


def header_field(text: str, name: str) -> str | None:
    m = re.search(rf"^\s*(?:#\s*|<!--\s*)?{name}:\s*(.+?)\s*(?:-->)?$", text, re.M | re.I)
    if not m:
        return None
    value = m.group(1).strip()
    return None if PLACEHOLDER.search(value) else value


def parse_date(value: str | None) -> dt.date | None:
    if not value:
        return None
    try:
        return dt.date.fromisoformat(value[:10])
    except ValueError:
        return None


# --------------------------------------------------------------------------- init

def cmd_init(target: Path, name: str | None) -> int:
    if target.exists() and any(target.iterdir()):
        print(f"{target} already exists and is not empty. Refusing to overwrite.")
        return 1
    if not TEMPLATE_DIR.exists():
        print(f"templates not found at {TEMPLATE_DIR}.")
        print("sixgates init needs the repository's templates/ folder. Run it from a clone installed with `pip install -e .`.")
        return 1
    name = name or target.name
    shutil.copytree(TEMPLATE_DIR, target, dirs_exist_ok=True)
    for path in target.rglob("*"):
        if path.is_file() and path.suffix in {".md", ".yaml", ".yml"}:
            text = path.read_text()
            text = text.replace("<working-name>", name).replace("<working name>", name).replace("<agent name>", name)
            path.write_text(text)
    (target / "evals" / "runs").mkdir(exist_ok=True)
    print(f"scaffolded {target} for agent {name!r}")
    print("next: book the one-hour session and fill gates/01-justify.md first.")
    return 0


# --------------------------------------------------------------------------- check

def check(agent_dir: Path) -> Report:
    r = Report()
    if not agent_dir.is_dir():
        r.fail("all", f"{agent_dir} is not a directory")
        return r

    # ---- the six artifacts
    for fname, numeral, title in GATES:
        path = agent_dir / "gates" / fname
        gate = f"{numeral} {title}"
        if not path.exists():
            r.fail(gate, f"gates/{fname} missing. A gate without an artifact was not passed.")
            continue
        text = path.read_text()
        if signed(text):
            r.ok(gate, f"gates/{fname} signed")
        else:
            r.fail(gate, f"gates/{fname} not signed, or the signature still has placeholders")
        leftovers = len(PLACEHOLDER.findall(text))
        if leftovers:
            r.warn(gate, f"gates/{fname} has {leftovers} unfilled placeholder(s)")

    # ---- config.yaml: tier, kill switch, levels, thresholds
    cfg_path = agent_dir / "config.yaml"
    cfg: dict = {}
    if not cfg_path.exists():
        r.fail("II Grade", "config.yaml missing")
    else:
        cfg = load_yaml(cfg_path)
        tier = cfg.get("risk_tier")
        if tier in (1, 2, 3, 4):
            r.ok("II Grade", f"risk_tier is {tier}")
        else:
            r.fail("II Grade", f"config.yaml risk_tier must be 1-4, got {tier!r}")
        if "kill_switch" in cfg and isinstance(cfg["kill_switch"], bool):
            r.ok("VI Run", f"kill_switch present ({'ON' if cfg['kill_switch'] else 'off'})")
            if cfg["kill_switch"]:
                r.warn("VI Run", "kill_switch is ON: the boundary halts every call")
        else:
            r.fail("VI Run", "config.yaml needs a boolean kill_switch")

    # ---- tools/catalog.yaml: every argument has a pen
    cat_path = agent_dir / "tools" / "catalog.yaml"
    tools: dict = {}
    if not cat_path.exists():
        r.fail("III Limit", "tools/catalog.yaml missing")
    else:
        cat = load_yaml(cat_path)
        tools = cat.get("tools") or {}
        if not isinstance(tools, dict) or not tools:
            r.fail("III Limit", "tools/catalog.yaml lists no tools")
        else:
            bad = []
            human_unprotected = []
            for tool, args in tools.items():
                if not isinstance(args, dict):
                    bad.append(f"{tool}: no arguments")
                    continue
                for arg, rule in args.items():
                    if not isinstance(rule, dict) or rule.get("pen") not in PENS:
                        bad.append(f"{tool}.{arg}: no pen")
                    elif rule["pen"] == "application" and not rule.get("source"):
                        bad.append(f"{tool}.{arg}: application pen without source")
                    elif rule["pen"] == "human" and "allowed" not in rule and "max_value" not in rule:
                        human_unprotected.append(f"{tool}.{arg}")
            n_args = sum(len(a) for a in tools.values() if isinstance(a, dict))
            if bad:
                r.fail("III Limit", "catalog: " + "; ".join(bad))
            else:
                r.ok("III Limit", f"catalog: {len(tools)} tool(s), {n_args} argument(s), every one has a pen")
            if human_unprotected:
                r.warn("III Limit", "human-pen arguments with no allowed set or limit: " + ", ".join(human_unprotected))
            if str(cat_path.read_text()).count("<") > 0 and PLACEHOLDER.search(cat_path.read_text()):
                r.warn("III Limit", "catalog still has placeholders")

    # ---- levels and thresholds line up with the catalog
    levels = cfg.get("levels") or {}
    thresholds = cfg.get("thresholds") or {}
    if tools and cfg:
        unknown = sorted(set(levels) - set(tools))
        missing = sorted(set(tools) - set(levels))
        if unknown:
            r.fail("V Prove", f"levels for tools not in catalog: {unknown}")
        if missing:
            r.warn("V Prove", f"tools with no level set (treated as 0): {missing}")
        # Promotion only means something for a tool a human has to approve. A tool whose
        # arguments are all application- or model-pen has no checkpoint to be released from.
        human_tools = {
            t for t, args in tools.items() if isinstance(args, dict)
            and any(isinstance(rule, dict) and rule.get("pen") == "human" for rule in args.values())
        }
        for tool, level in levels.items():
            if level not in (0, 1, 2):
                r.fail("V Prove", f"level for {tool} must be 0, 1 or 2, got {level!r}")
            elif level > 0 and tool in human_tools and tool not in thresholds:
                r.fail("V Prove", f"{tool} has a human-pen argument and is at level {level} with no thresholds in config.yaml")
        if levels and not any(f.gate == "V Prove" and f.level == "FAIL" for f in r.findings):
            promoted = sorted(t for t in human_tools if levels.get(t, 0) > 0)
            r.ok("V Prove", f"levels are 0-2; human-pen tools above level 0 with thresholds: {promoted or 'none yet'}")

    # ---- frozen sets
    evals = agent_dir / "evals"
    sets = sorted(evals.glob("set-*.jsonl")) if evals.exists() else []
    if not sets:
        r.warn("V Prove", "no evals/set-*.jsonl yet. Nothing can be promoted without one.")
    for s in sets:
        side = s.with_suffix(".sha256")
        if not side.exists():
            r.fail("V Prove", f"{s.name} is not frozen (no .sha256). Run freeze.py.")
            continue
        recorded = side.read_text().split()[0]
        actual = hashlib.sha256(s.read_bytes()).hexdigest()
        if recorded == actual:
            r.ok("V Prove", f"{s.name} frozen, hash matches")
        else:
            r.fail("V Prove", f"{s.name} changed since it was frozen. Frozen means frozen.")
    runs = list((evals / "runs").glob("*.json")) if (evals / "runs").exists() else []
    human_promoted = [t for t, l in levels.items() if l > 0 and t in tools and any(
        isinstance(rule, dict) and rule.get("pen") == "human" for rule in (tools[t] or {}).values())]
    if human_promoted and not runs:
        r.fail("V Prove", f"{human_promoted} above level 0 but evals/runs/ has no run record")

    # ---- prompt header: owner, last-reviewed, last-shrunk
    prompt_rel = (cfg.get("prompt") or {}).get("path", "prompts/system.md")
    prompt = agent_dir / prompt_rel
    if not prompt.exists():
        r.fail("VI Run", f"{prompt_rel} missing")
    else:
        text = prompt.read_text()
        owner = header_field(text, "owner")
        if owner:
            r.ok("VI Run", f"prompt owner: {owner}")
        else:
            r.fail("VI Run", f"{prompt_rel} has no owner: line. Nothing enters the system without an owner.")
        shrunk = parse_date(header_field(text, "last-shrunk"))
        if shrunk is None:
            r.warn("VI Run", f"{prompt_rel} has no last-shrunk: date")
        else:
            age = (dt.date.today() - shrunk).days
            if age > 45:
                r.warn("VI Run", f"prompt last shrunk {age} days ago. The monthly deletion pass is overdue.")
            else:
                r.ok("VI Run", f"prompt last shrunk {age} days ago")

    # ---- skills provenance
    skills = agent_dir / "skills"
    if skills.exists():
        for f in skills.glob("*.md"):
            if f.name.lower() == "readme.md":
                continue
            text = f.read_text()
            if not header_field(text, "reviewed-by"):
                r.fail("VI Run", f"skills/{f.name} has no reviewed-by. Unreviewed means inactive.")
            else:
                r.ok("VI Run", f"skills/{f.name} reviewed")

    # ---- README owner
    readme = agent_dir / "README.md"
    if readme.exists():
        text = readme.read_text()
        if re.search(r"Owner on the pager.*\|\s*<", text) or "Owner on the pager" in text and PLACEHOLDER.search(text.split("Owner on the pager", 1)[1].split("\n", 1)[0]):
            r.fail("VI Run", "README has no named owner on the pager")
        elif "Owner on the pager" in text:
            r.ok("VI Run", "README names an owner on the pager")
    return r


def print_report(agent_dir: Path, r: Report) -> None:
    cfg = agent_dir / "config.yaml"
    tier = load_yaml(cfg).get("risk_tier", "?") if cfg.exists() else "?"
    print(f"six gates check · {agent_dir} · tier {tier}")
    print()
    for _, numeral, title in GATES:
        gate = f"{numeral} {title}"
        status = r.gate_status(gate)
        mark = {"PASS": "✓", "WARN": "!", "FAIL": "✗"}[status]
        print(f"  {mark} {numeral:<4}{title:<9}{status}")
        for f in r.findings:
            if f.gate == gate and f.level != "PASS":
                print(f"           {f.level.lower()}: {f.message}")
    other = [f for f in r.findings if f.gate == "all"]
    for f in other:
        print(f"  ✗ {f.message}")
    print()
    fails = sum(1 for f in r.findings if f.level == "FAIL")
    warns = sum(1 for f in r.findings if f.level == "WARN")
    verdict = "not passed" if r.failed else "passed"
    print(f"{verdict}: {fails} failing check(s), {warns} warning(s)")
    if r.failed:
        print("A gate that leaves no signed artifact was not passed. It was waved.")


# --------------------------------------------------------------------------- badge

def badge_svg(label: str, value: str, colour: str) -> str:
    def width(s: str) -> int:
        return int(len(s) * 6.6 + 20)

    lw, vw = width(label), width(value)
    total = lw + vw
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{total}" height="20" role="img" aria-label="{label}: {value}">
<title>{label}: {value}</title>
<linearGradient id="s" x2="0" y2="100%"><stop offset="0" stop-color="#fff" stop-opacity=".1"/><stop offset="1" stop-opacity=".1"/></linearGradient>
<clipPath id="r"><rect width="{total}" height="20" rx="3" fill="#fff"/></clipPath>
<g clip-path="url(#r)"><rect width="{lw}" height="20" fill="#251D16"/><rect x="{lw}" width="{vw}" height="20" fill="{colour}"/><rect width="{total}" height="20" fill="url(#s)"/></g>
<g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="11">
<text x="{lw / 2:.1f}" y="14">{label}</text><text x="{lw + vw / 2:.1f}" y="14">{value}</text></g>
</svg>'''


TIER_COLOURS = {1: "#7B5A3A", 2: "#9C3A21", 3: "#B4321E", 4: "#7A1E14"}


def cmd_badge(agent_dir: Path, out: Path | None) -> int:
    cfg_path = agent_dir / "config.yaml"
    if not cfg_path.exists():
        print("config.yaml missing")
        return 1
    cfg = load_yaml(cfg_path)
    tier = cfg.get("risk_tier", "?")
    levels = cfg.get("levels") or {}
    if levels:
        lo, hi = min(levels.values()), max(levels.values())
        level_txt = f"L{lo}" if lo == hi else f"L{lo}–L{hi}"
    else:
        level_txt = "L0"
    r = check(agent_dir)
    state = "gated" if not r.failed else "gates open"
    value = f"Tier {tier} · {level_txt} · {state}"
    svg = badge_svg("Six Gates", value, TIER_COLOURS.get(tier, "#8A7A69"))
    out = out or (agent_dir / "six-gates-badge.svg")
    out.write_text(svg)
    print(f"wrote {out}")
    print()
    print("Add to your README:")
    print(f"[![Six Gates]({out.as_posix()})](https://github.com/bhargava-dev-ai/six-gates)")
    return 0


# --------------------------------------------------------------------------- main

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="sixgates", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="scaffold an agent folder from the templates")
    p_init.add_argument("target", type=Path)
    p_init.add_argument("--name", help="agent name (defaults to the folder name)")

    p_check = sub.add_parser("check", help="verify the ledger and report each gate")
    p_check.add_argument("agent_dir", type=Path)

    p_badge = sub.add_parser("badge", help="write a README badge from config.yaml")
    p_badge.add_argument("agent_dir", type=Path)
    p_badge.add_argument("--out", type=Path)

    args = ap.parse_args(argv)
    if args.cmd == "init":
        return cmd_init(args.target, args.name)
    if args.cmd == "check":
        r = check(args.agent_dir)
        print_report(args.agent_dir, r)
        return 1 if r.failed else 0
    if args.cmd == "badge":
        return cmd_badge(args.agent_dir, args.out)
    return 2


if __name__ == "__main__":
    sys.exit(main())
