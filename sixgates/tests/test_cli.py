"""Tests for the sixgates command. Run with ``pytest sixgates -q`` from the repository root."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
EXAMPLE = REPO / "examples" / "expense-triage"


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-m", "sixgates", *args], cwd=REPO, capture_output=True, text=True)


def test_check_passes_on_the_worked_example():
    p = run("check", str(EXAMPLE))
    assert p.returncode == 0, p.stdout + p.stderr
    assert "passed: 0 failing" in p.stdout
    for numeral in ("I ", "II ", "III ", "IV ", "V ", "VI "):
        assert f"✓ {numeral}" in p.stdout


def test_init_scaffolds_and_check_reports_unsigned_gates(tmp_path):
    target = tmp_path / "agents" / "demo"
    p = run("init", str(target), "--name", "demo")
    assert p.returncode == 0, p.stdout + p.stderr
    assert (target / "gates" / "01-justify.md").exists()
    assert "demo" in (target / "README.md").read_text()

    p = run("check", str(target))
    assert p.returncode == 1
    assert "not signed" in p.stdout
    assert "was waved" in p.stdout


def test_init_refuses_to_overwrite(tmp_path):
    target = tmp_path / "agents" / "demo"
    target.mkdir(parents=True)
    (target / "keep.txt").write_text("x")
    p = run("init", str(target))
    assert p.returncode == 1
    assert "Refusing" in p.stdout


def test_check_fails_when_a_frozen_set_is_edited(tmp_path):
    import shutil

    target = tmp_path / "expense-triage"
    shutil.copytree(EXAMPLE, target)
    s = target / "evals" / "set-v1.jsonl"
    s.write_text(s.read_text() + "\n")
    p = run("check", str(target))
    assert p.returncode == 1
    assert "changed since it was frozen" in p.stdout


def test_check_fails_on_argument_without_pen(tmp_path):
    import shutil

    target = tmp_path / "expense-triage"
    shutil.copytree(EXAMPLE, target)
    cat = target / "tools" / "catalog.yaml"
    cat.write_text(cat.read_text().replace("{ pen: model, type: string, max_length: 2000 }", "{ type: string }"))
    p = run("check", str(target))
    assert p.returncode == 1
    assert "no pen" in p.stdout


def test_badge_is_written(tmp_path):
    out = tmp_path / "badge.svg"
    p = run("badge", str(EXAMPLE), "--out", str(out))
    assert p.returncode == 0, p.stdout + p.stderr
    svg = out.read_text()
    assert svg.startswith("<svg") and "Six Gates" in svg and "Tier 2" in svg and "gated" in svg
