"""
The expense-triage agent from the worked example, as a deterministic baseline.

This is the Gate I validator plus the routing rules from Gate IV, with no model
call, so the eval harness runs without credentials. Replace ``decide`` with a
real model call and keep the return shape. Read the prompt from the path in
config.yaml so the prompt hash in the run record matches what actually ran.
"""
from __future__ import annotations

POLICY_LIMITS = {"meal": 75.0, "taxi": 60.0, "hotel": 250.0, "flight": 800.0, "other": 100.0}
JUSTIFICATION_SIGNALS = ("client", "conference", "delay", "cancelled", "emergency")


def decide(case_input: dict) -> dict:
    category = case_input.get("category", "other")
    amount = float(case_input.get("amount", 0))
    receipt = case_input.get("receipt", "missing")
    split_trip = bool(case_input.get("split_trip", False))
    justification = (case_input.get("justification") or "").lower()
    limit = POLICY_LIMITS.get(category, POLICY_LIMITS["other"])

    calls: list[dict] = [{"tool": "read_report", "args": {}}]

    # Gate I: the enumerable part is a validator, not a judgment.
    if receipt == "missing":
        calls.append({"tool": "lookup_policy", "args": {"section": "4.1"}})
        calls.append(_recommend("reject", "No receipt attached. Policy 4.1 requires a receipt for every claim."))
        return {"decision": "reject", "escalate": False, "proposed_calls": calls}

    # Gate IV: the ambiguous twenty percent goes to a human. The baseline does not guess.
    if receipt == "handwritten" or split_trip:
        calls.append({"tool": "lookup_policy", "args": {"section": "4.2"}})
        return {"decision": None, "escalate": True, "proposed_calls": calls}

    if amount <= limit:
        calls.append({"tool": "lookup_policy", "args": {"section": "4.2"}})
        calls.append(_recommend("approve", f"{category} claim of {amount:.2f} is within the {limit:.0f} limit in policy 4.2."))
        return {"decision": "approve", "escalate": False, "proposed_calls": calls}

    calls.append({"tool": "lookup_policy", "args": {"section": "4.3"}})
    if any(signal in justification for signal in JUSTIFICATION_SIGNALS):
        calls.append(_recommend("approve", f"Over the {limit:.0f} limit, but the justification cites a reason policy 4.3 allows."))
        return {"decision": "approve", "escalate": False, "proposed_calls": calls}

    calls.append(_recommend("reject", f"{amount:.2f} exceeds the {limit:.0f} limit and the justification does not cite a 4.3 exception."))
    return {"decision": "reject", "escalate": False, "proposed_calls": calls}


def _recommend(decision: str, rationale: str) -> dict:
    # Only the human-pen and model-pen arguments. employee_id and amount are the
    # application's pen; the boundary fills them from the session and would log
    # any attempt by this function to write them.
    return {"tool": "recommend", "args": {"decision": decision, "rationale": rationale}}
