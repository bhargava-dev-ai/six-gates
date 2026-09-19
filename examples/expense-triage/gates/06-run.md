# Gate VI · Run

**Who maintains the system that maintains itself?**

Agent: expense-triage · Tier: 2

## Owner

| | |
|---|---|
| On the pager | the engineer on the platform-eng rota |
| Backup | finance platform lead |
| Rota | platform-eng weekly rotation |

## Ledger

Location: `examples/expense-triage/`
Contents: `prompts/` · `tools/catalog.yaml` · `config.yaml` · `gates/` · `evals/`
Every file carries `owner:` and `last-reviewed:` in its header.

## Provenance rule for agent-authored content

None yet. If the agent is later allowed to suggest prompt changes or write skills, each arrives as a pull request with a provenance header and is inactive until the platform lead reviews it.

## Cadence

| | | |
|---|---|---|
| Escalation review | weekly, Friday | reader: owner on the pager |
| Deletion pass | monthly, first Monday | quota: at least one item removed |
| Re-grade (Gate II) | quarterly, or on trigger | finance controller |
| Off-switch test | quarterly | owner |

## Off switch

| | |
|---|---|
| Mechanism | `config.yaml: kill_switch` read by the boundary before every call |
| In-flight behaviour | drafts preserved in the queue, no tool executes, reviewers see a banner |
| First test | second week of production |

Signed: operations · Date: 2026-09-18

## Deletion log

| Date | Removed | Why | By |
|---|---|---|---|

## Off-switch tests

| Date | Result | Notes | By |
|---|---|---|---|
