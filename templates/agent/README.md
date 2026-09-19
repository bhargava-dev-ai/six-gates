# <agent name>

**Request as asked:** "<one paragraph, verbatim, from whoever asked>"

| | |
|---|---|
| Risk tier (Gate II) | <1-4> |
| Owner on the pager (Gate VI) | <name> · backup <name> |
| Status | <session scheduled / at Level 0 / promoting / stopped at Gate <n>> |
| Session date | <yyyy-mm-dd> |

## Current levels per tool (Gate V)

| Tool | Level | Since | Evidence |
|---|---|---|---|
| <tool> | 0 · suggestion only | <date> | evals/runs/<file> |

Levels: 0 suggestion only · 1 human approved · 2 autonomous, sampled. Promotion needs the signature named in `gates/02-grade.md`. Demotion is automatic on any harm-rate event.

## Folder

```
gates/          the six signed artifacts. A gate without a signed file was not passed.
config.yaml     risk_tier, levels per tool, thresholds, kill_switch. Read at runtime.
prompts/        system prompt and any sub-prompts. Owner and last-shrunk date in the header.
skills/         anything the agent uses as a skill. Provenance header on each file.
tools/          catalog.yaml: every reachable tool, every argument, its pen. Read at runtime.
evals/          frozen set + sha256 sidecar, and one run record per eval run.
```

## Cadence (Gate VI)

- Escalation review: weekly, <day>, reader <owner>
- Deletion pass: monthly, <day>, quota at least one item removed, logged in `gates/06-run.md`
- Off-switch test: quarterly, last tested <date>, result <pass/fail>
- Re-grade (Gate II): quarterly, or on any trigger listed in the guide
