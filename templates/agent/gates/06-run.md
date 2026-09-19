# Gate VI · Run

**Who maintains the system that maintains itself?**

Agent: <working name> · Tier: <from Gate II>

## Owner

| | |
|---|---|
| On the pager | <name> |
| Backup | <name> |
| Rota | <reference> |

A person, not a team. Teams do not wake up at 2am.

## Ledger

Location: `<repo>/agents/<name>/`
Contents: `prompts/` · `skills/` · `tools/catalog.yaml` · `config.yaml` · `gates/`
Every file carries `owner:` and `last-reviewed:` in its header.

## Provenance rule for agent-authored content

Anything the agent writes about itself (skills, memory entries, prompt suggestions) carries a header: producer, model version, timestamp, triggering case. It is inactive until reviewed by <name or role>. Review is a pull request.

## Cadence

| | | |
|---|---|---|
| Escalation review | weekly, <day> | reader <owner> |
| Deletion pass | monthly, <day> | quota: at least one item removed |
| Re-grade (Gate II) | quarterly, or on trigger | risk owner |
| Off-switch test | quarterly | owner |

## Off switch

| | |
|---|---|
| Mechanism | `config.yaml: kill_switch` checked at the tool boundary before every call |
| In-flight behaviour | <drafts preserved, executions halted, queue frozen> |
| First test | <date> |

Signed: <operations> · Date: <yyyy-mm-dd>

## Deletion log

| Date | Removed | Why | By |
|---|---|---|---|

## Off-switch tests

| Date | Result | Notes | By |
|---|---|---|---|
