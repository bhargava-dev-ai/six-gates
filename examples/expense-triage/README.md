# expense-triage

**Request as asked:** "Can we get an AI agent to handle expense reports?"

| | |
|---|---|
| Risk tier (Gate II) | 2 · analyst augmentation. Reads everything, decides nothing. |
| Owner on the pager (Gate VI) | platform-eng on-call rota · backup: finance platform lead |
| Status | at Level 0 for `recommend` · baseline in place |
| Session date | 2026-09-18 |

This is the worked example from *Running the Six Gates*, as a folder you can run:

```bash
pip install -r reference/requirements.txt
pytest reference/boundary -q
python reference/evals/freeze.py examples/expense-triage/evals/set-v1.jsonl
python reference/evals/run_eval.py --agent examples/expense-triage --promote recommend --to 1
```

`agent.py` is the deterministic baseline from Gate I: the policy-limit validator plus the routing rule that sends handwritten receipts and split trips to a human. It is what any model has to beat at Gate V. Case c-0011 is there to show it losing: an over-limit meal with a plausible justification, "dinner with the vendor's account manager", that the baseline's keyword list does not catch. That is the judgment slice the agent is justified for, and the first case a model has to get right to earn its place.

## Current levels per tool

| Tool | Level | Since | Evidence |
|---|---|---|---|
| read_report | 2 | 2026-09-18 | application pen only; nothing to promote |
| lookup_policy | 2 | 2026-09-18 | model pen from an allowlist; nothing to promote |
| recommend | 0 | 2026-09-18 | see `evals/runs/` |

## Folder

```
gates/          six signed artifacts, filled in
config.yaml     tier 2, levels, thresholds, kill switch
prompts/        the prompt a model would receive
tools/          catalog.yaml with the pens
evals/          16 frozen cases, sha256, run records
agent.py        the baseline
```
