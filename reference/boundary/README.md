# Reference tool boundary (Gate III)

A small, dependency-light implementation of the three pens. It reads `tools/catalog.yaml` and `config.yaml` from an agent folder and is the only thing that executes tools.

```python
from boundary import Boundary, Session, Approval

boundary = Boundary("agents/expense-triage", tools={"read_report": read_report, "lookup_policy": lookup_policy, "recommend": recommend}, audit=audit_log.write)

session = Session(user="reviewer@co", values={"report_id": "R-1042", "employee_id": "E-77", "claimed_amount": 84.20},
                  allowlists={"policy_sections": policy.section_ids()})

# The model proposed this call. The boundary decides what happens.
outcome = boundary.call("recommend", model_proposal.args, session, approvals=approvals_for(session))

if outcome.kind == "escalated":
    checkpoint.enqueue(outcome)          # Gate IV: the human approves, rejects, or edits
elif outcome.kind == "rejected":
    log.warning(outcome.detail)          # Gate V: rejections count toward the harm rate
elif outcome.kind == "halted":
    ...                                  # Gate VI: the kill switch is on
```

What it enforces:

| Situation | Outcome |
|---|---|
| Model supplies a value for an application-pen argument | value ignored, session value used, note in audit record |
| Human-pen argument without a covering approval | `escalated`, nothing executes |
| Approval for a different value, tool, argument, or expired | `escalated` |
| Model-pen value fails type, length, or allowlist | `rejected` |
| Argument not in the catalog | `rejected` |
| Tool not in the catalog | `rejected` |
| `kill_switch: true` in config | `halted`, checked before anything else |
| A registered tool is missing from the catalog | refuses to start |

Every call writes one audit record with the pens, the catalog hash, the actor, the model's arguments, and the final arguments. Gate V reads these; Gate VI reviews them.

Run the tests:

```bash
pip install pyyaml pytest && pytest reference/boundary -q
```

This is a reference, not a library. Copy it into your codebase and adapt it. The shape that matters is: the catalog is data the boundary reads, the model never sees it, and approvals are specific to a value.
