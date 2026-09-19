# Gate IV · Build

**What is the smallest supervised loop that could work?**

Agent: <working name> · Tier: <from Gate II>

## The loop

```
[ agent drafts ] → [ human approves: <who> ] → [ execute + log ]
```

Human-pen arguments routed to the checkpoint: <list from Gate III>
Everything else passes straight to execute, with logging.

## The cascade

| Step | Handled by | Because |
|---|---|---|
| <step> | code | rubric fully writable |
| <step> | small model | rubric writable, fuzzy inputs |
| <step> | frontier model | judgment on <which inputs> |
| <step> | human | below confidence <threshold> or outside catalog |

## Agents

Count: 1

If more than one, the justification by context size or tier difference: <…>

## Logging

| | |
|---|---|
| What | tool calls with pens · model input and output · approvals and rejections with actor and reason · escalations |
| Where | <log location> |
| Retention | <from Gate II> |

## Escalation

| | |
|---|---|
| Queue | <location> |
| Owner | <name> |
| Response time | <e.g. 4 business hours> |

## The approval screen

Shows: the draft · the evidence or policy cited · the exact tool call with each argument's pen · approve / reject with reason / edit and approve.

Signed: <engineering lead> · Date: <yyyy-mm-dd>
