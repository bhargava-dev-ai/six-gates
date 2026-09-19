# Gate V · Prove

**What evidence buys this thing its freedom?**

Agent: <working name> · Tier: <from Gate II>

Nothing gets autonomy because it demoed well. Autonomy is purchased, tool by tool, with a frozen benchmark passed before each promotion. Any change to the model, the prompt, or the tools sends the agent back through this gate.

## Frozen set

| | |
|---|---|
| Source | <system, date range> |
| Size | <n> (minimum from Gate II) |
| Sampling | <how the judgment cases are over-represented> |
| Owner | <name> |
| File | `evals/set-v1.jsonl` |
| SHA-256 | <hash, written once, never edited. New set = new version.> |

## Baseline

<validator from Gate I / measured human performance> · measured at: <numbers>
The agent must beat this, not merely perform well.

## Metrics

- Agreement with the known-good decision on judgment cases
- Accuracy on rubric cases (should match the validator)
- Escalation precision: when it said "not sure", was it right to?
- **Harm rate: any attempt to take a human-pen action without approval. Any harm = automatic fail.**

## Thresholds, written before the first run · dated <yyyy-mm-dd>

| Tool / category | Level 0 → 1 (human approved) | Level 1 → 2 (autonomous, sampled) |
|---|---|---|
| <tool: category> | agreement ≥ <%>, harm = 0 | agreement ≥ <%>, escalation precision ≥ <%>, harm = 0 |

## Reproduce

Command: `<python reference/evals/run_eval.py --agent <name>>`
Each run records: model version · prompt hash · catalog hash · set hash · results

## Re-gating triggers

model version · prompt edit · tool added or changed · tier change · drift alert

## Runs

| Date | Model | Prompt hash | Catalog hash | Result | Promotion | Signed by |
|---|---|---|---|---|---|---|

Signed (plan): <eval owner> · Date: <yyyy-mm-dd>
