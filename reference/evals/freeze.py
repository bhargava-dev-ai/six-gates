"""
Gate V. Freeze an eval set.

    python reference/evals/freeze.py agents/<name>/evals/set-v1.jsonl

Writes ``set-v1.sha256`` beside the set. Refuses to overwrite an existing hash
that differs: a frozen set is never edited. Make ``set-v2.jsonl`` instead.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sidecar(path: Path) -> Path:
    return path.with_suffix(".sha256")


def verify(path: Path) -> str:
    """Return the hash if the set matches its sidecar. Raise if it was edited or never frozen."""
    side = sidecar(path)
    if not side.exists():
        raise SystemExit(f"{path.name} is not frozen. Run freeze.py first.")
    recorded = side.read_text().split()[0]
    actual = sha256_file(path)
    if recorded != actual:
        raise SystemExit(
            f"{path.name} has changed since it was frozen.\n"
            f"  recorded {recorded}\n  actual   {actual}\n"
            "A frozen set is never edited. Create a new version instead."
        )
    return actual


def freeze(path: Path) -> str:
    if not path.exists():
        raise SystemExit(f"no such file: {path}")
    actual = sha256_file(path)
    side = sidecar(path)
    if side.exists():
        recorded = side.read_text().split()[0]
        if recorded != actual:
            raise SystemExit(
                f"{side.name} already exists with a different hash. Refusing to overwrite.\n"
                "Frozen means frozen. Save your changes as a new version."
            )
        print(f"already frozen: {actual}")
        return actual
    side.write_text(f"{actual}  {path.name}\n")
    print(f"frozen: {actual}  {path.name}")
    return actual


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    freeze(Path(sys.argv[1]))
