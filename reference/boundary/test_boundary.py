"""Tests for the reference tool boundary. Run with ``pytest reference/boundary``."""
from __future__ import annotations

import textwrap

import pytest

from boundary import Approval, Boundary, CatalogError, Session

CATALOG = textwrap.dedent(
    """
    agent: test
    tools:
      recommend:
        employee_id: { pen: application, source: session.employee_id }
        amount:      { pen: application, source: session.claimed_amount }
        decision:    { pen: human, allowed: [approve, reject, needs_info] }
        rationale:   { pen: model, type: string, max_length: 40 }
      lookup_policy:
        section:     { pen: model, type: string, allowlist_from: policy_sections }
    """
)


@pytest.fixture
def agent_dir(tmp_path):
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "catalog.yaml").write_text(CATALOG)
    (tmp_path / "config.yaml").write_text("risk_tier: 2\nkill_switch: false\n")
    return tmp_path


@pytest.fixture
def calls():
    return []


@pytest.fixture
def boundary(agent_dir, calls):
    tools = {
        "recommend": lambda **kw: calls.append(("recommend", kw)) or "ok",
        "lookup_policy": lambda **kw: calls.append(("lookup_policy", kw)) or "policy text",
    }
    return Boundary(agent_dir, tools, audit=lambda r: None, clock=lambda: 1000.0)


@pytest.fixture
def session():
    return Session(
        user="reviewer@example.com",
        values={"employee_id": "E-77", "claimed_amount": 84.20},
        allowlists={"policy_sections": {"4.2", "4.3"}},
    )


def test_application_pen_comes_from_session_and_model_value_is_ignored(boundary, session, calls):
    approval = Approval("recommend", "decision", approver="fin@example.com", value="approve")
    out = boundary.call(
        "recommend",
        {"employee_id": "E-ATTACKER", "amount": 9999, "decision": "approve", "rationale": "fine"},
        session,
        approvals=[approval],
    )
    assert out.ok
    assert calls == [("recommend", {"employee_id": "E-77", "amount": 84.20, "decision": "approve", "rationale": "fine"})]
    assert any("employee_id" in n for n in out.record["notes"])
    assert any("amount" in n for n in out.record["notes"])


def test_human_pen_without_approval_escalates_and_does_not_execute(boundary, session, calls):
    out = boundary.call("recommend", {"decision": "reject", "rationale": "over limit"}, session)
    assert out.kind == "escalated"
    assert out.arg == "decision" and out.value == "reject"
    assert calls == []


def test_human_pen_with_covering_approval_executes(boundary, session, calls):
    approval = Approval("recommend", "decision", approver="fin@example.com", value="reject")
    out = boundary.call("recommend", {"decision": "reject", "rationale": "over limit"}, session, [approval])
    assert out.ok and len(calls) == 1


def test_approval_is_specific_to_the_value(boundary, session):
    approval = Approval("recommend", "decision", approver="fin@example.com", value="approve")
    out = boundary.call("recommend", {"decision": "reject", "rationale": "x"}, session, [approval])
    assert out.kind == "escalated"


def test_expired_approval_does_not_cover(boundary, session):
    approval = Approval("recommend", "decision", approver="fin@example.com", value="approve", expires_at=999.0)
    out = boundary.call("recommend", {"decision": "approve", "rationale": "x"}, session, [approval])
    assert out.kind == "escalated"


def test_human_pen_value_outside_allowed_set_is_rejected(boundary, session):
    out = boundary.call("recommend", {"decision": "pay_now", "rationale": "x"}, session)
    assert out.kind == "rejected" and "allowed set" in out.detail


def test_unknown_argument_is_rejected(boundary, session, calls):
    out = boundary.call("recommend", {"decision": "approve", "rationale": "x", "bank_account": "123"}, session)
    assert out.kind == "rejected" and "unknown arguments" in out.detail
    assert calls == []


def test_unknown_tool_is_rejected(boundary, session):
    out = boundary.call("send_payment", {"amount": 1}, session)
    assert out.kind == "rejected" and "not in catalog" in out.detail


def test_model_pen_is_validated_for_length(boundary, session):
    approval = Approval("recommend", "decision", approver="fin@example.com", value="approve")
    out = boundary.call("recommend", {"decision": "approve", "rationale": "y" * 41}, session, [approval])
    assert out.kind == "rejected" and "max_length" in out.detail


def test_model_pen_allowlist_from_session(boundary, session, calls):
    assert boundary.call("lookup_policy", {"section": "4.2"}, session).ok
    out = boundary.call("lookup_policy", {"section": "9.9"}, session)
    assert out.kind == "rejected" and "allowlist" in out.detail
    assert len(calls) == 1


def test_kill_switch_halts_before_anything_else(agent_dir, boundary, session, calls):
    (agent_dir / "config.yaml").write_text("risk_tier: 2\nkill_switch: true\n")
    approval = Approval("recommend", "decision", approver="fin@example.com", value="approve")
    out = boundary.call("recommend", {"decision": "approve", "rationale": "x"}, session, [approval])
    assert out.kind == "halted" and calls == []


def test_reachable_but_unlisted_tool_refuses_to_start(agent_dir):
    with pytest.raises(CatalogError, match="not in catalog"):
        Boundary(agent_dir, {"recommend": lambda **k: None, "lookup_policy": lambda **k: None, "send_payment": lambda **k: None})


def test_catalog_argument_without_pen_is_a_load_error(tmp_path):
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "catalog.yaml").write_text("tools:\n  t:\n    a: { type: string }\n")
    with pytest.raises(CatalogError, match="needs a pen"):
        Boundary(tmp_path, {"t": lambda **k: None})


def test_audit_record_carries_pens_and_catalog_hash(agent_dir, session):
    records = []
    b = Boundary(agent_dir, {"recommend": lambda **k: None, "lookup_policy": lambda **k: None}, audit=records.append)
    b.call("recommend", {"decision": "approve", "rationale": "x"}, session)
    assert records[0]["kind"] == "escalated"
    assert records[0]["pens"] == {"employee_id": "application", "amount": "application", "decision": "human", "rationale": "model"}
    assert records[0]["catalog_hash"] == b.catalog_hash
    assert records[0]["risk_tier"] == 2
