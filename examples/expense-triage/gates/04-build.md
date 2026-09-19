# Gate IV · Build

**What is the smallest supervised loop that could work?**

Agent: expense-triage · Tier: 2

## The loop

```
[ agent drafts a recommendation citing policy lines ] → [ reviewer approves / rejects / edits ] → [ decision recorded + logged ]
```

Human-pen arguments routed to the checkpoint: `recommend.decision`

## The cascade

| Step | Handled by | Because |
|---|---|---|
| Receipt present, category limit, category-receipt match | code (the validator) | rubric fully writable |
| Receipt type classification (printed / handwritten / missing) | small model | rubric writable, fuzzy input |
| Reasonableness of an over-limit justification | frontier model | judgment on free text |
| Handwritten receipts and split trips | human | outside what the eval can yet cover |

## Agents

Count: 1

## Logging

| | |
|---|---|
| What | tool calls with pens · model input and output · reviewer approvals, rejections with reason, edits · escalations |
| Where | finance audit store, `agent=expense-triage` |
| Retention | 1 year |

## Escalation

| | |
|---|---|
| Queue | expense-review / needs-human |
| Owner | expense team lead |
| Response time | 4 business hours |

## The approval screen

Shows the recommendation, the policy lines cited, the tool call with pens visible (employee_id and amount from the system, decision awaiting the reviewer, rationale from the model), and three controls: approve, reject with reason, edit and approve.

Signed: engineering lead · Date: 2026-09-18
