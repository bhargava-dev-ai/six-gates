# Gate III · Limit

**Who is allowed to write what?**

Agent: expense-triage · Tier: 2

This file mirrors `tools/catalog.yaml`. If they disagree, the catalog wins and this file is wrong.

## Tool catalog

| Tool | Argument | Pen | Source / validation / approval |
|---|---|---|---|
| read_report | report_id | application | `session.report_id` |
| lookup_policy | section | model | allowlist of policy section ids from the session |
| recommend | employee_id | application | `session.employee_id` |
| recommend | amount | application | `session.claimed_amount` |
| recommend | decision | human | approval per call; allowed values approve, reject, needs_info |
| recommend | rationale | model | string, max 2000 characters, rendered as plain text |

Tools reachable by the runtime but not in this catalog: none. The boundary refuses to start if a registered tool is missing from the catalog.

## Enforcement

| | |
|---|---|
| Location | `reference/boundary/boundary.py`, instantiated on this folder |
| Unknown arguments | rejected and logged |
| Read scope | as the reviewer, with the reviewer's access to reports |

Signed: security review · Date: 2026-09-18

## Catalog changes

| Date | Change | Re-eval run | Signed |
|---|---|---|---|
