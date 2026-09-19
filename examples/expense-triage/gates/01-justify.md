# Gate I · Justify

**Should this be an agent at all?**

Agent: expense-triage
Request as asked: "Can we get an AI agent to handle expense reports?"
Good output, in the requester's words: "Reviewers stop spending their mornings on reports that are obviously fine."

## The checklist we tried to write

| Bullet | Column |
|---|---|
| Receipt attached | validator |
| Amount within the category limit in policy 4.2 | validator |
| Category matches the receipt type | validator |
| Handwritten receipt is genuine | judgment |
| Split trip allocated sensibly across cost centres | judgment |
| Out-of-policy amount has a reasonable business justification | judgment |

## The sentence

> This must be an agent because the decision cannot be specified in advance, specifically because:
> whether an out-of-policy claim is reasonable depends on a free-text business justification that policy cannot anticipate, and whether a handwritten receipt or split trip is legitimate depends on context that is not in any field.

## The split

| | |
|---|---|
| Validator handles | receipt presence, category limits, category-receipt match · owner: finance platform lead |
| Agent handles | handwritten receipts, split trips, over-limit claims with justification · about 20% of reports |

## Decision

- [x] Proceed to Gate II
- [ ] Build the validator only.

Signed: finance product owner, architect · Date: 2026-09-18
