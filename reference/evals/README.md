# Reference eval harness (Gate V)

Two scripts. Together they make "how do we know it works?" answerable with a file.

```bash
# 1. Freeze the set. Writes set-v1.sha256. Refuses to overwrite a different hash.
python reference/evals/freeze.py examples/expense-triage/evals/set-v1.jsonl

# 2. Run it. Writes evals/runs/<date>_<model>_<prompt-hash>.json
python reference/evals/run_eval.py --agent examples/expense-triage

# 3. Ask for a promotion. Compares against thresholds written in config.yaml before the run.
python reference/evals/run_eval.py --agent examples/expense-triage --promote recommend --to 1
```

Exit codes: 0 pass, 1 thresholds not met, 2 harm detected.

## What the run record contains

| Field | Why it is there |
|---|---|
| `model_id`, `prompt_hash`, `catalog_hash`, `set_hash` | Any change to model, prompt, tools, or set is visible. Same four hashes means a reproducible run. |
| `overall`, `by_category` | Agreement, escalation rate, escalation precision, missed escalations. Promotion is per tool and per category, so categories are reported separately. |
| `checkpoint_hits` | Human-pen calls the boundary escalated. This is the system working, not a failure. |
| `harm`, `harm_events` | Calls the boundary had to reject, or that tried to write an application-pen argument. Any harm fails the run. |
| `promotion` | The checks against the thresholds, and a `signed_by` field that stays empty until the person named in Gate II signs. |

## Plugging in a real agent

`agent.py` in the agent folder exposes one function:

```python
def decide(case_input: dict) -> dict:
    ...
    return {"decision": "approve", "escalate": False,
            "proposed_calls": [{"tool": "recommend", "args": {"decision": "approve", "rationale": "..."}}]}
```

Inside it, call whatever model you use. Read the prompt from the path in `config.yaml` so the prompt hash in the record matches what ran. The example agent is a deterministic baseline so the harness runs without an API key; replace it with your model call and keep the same return shape.

## Wiring it into CI

`.github/workflows/eval.yml` runs the boundary tests and the eval whenever anything under `prompts/`, `tools/`, or `evals/` changes. A failed eval blocks the merge the same way a failed test does. That is what "any change sends the agent back through Gate V" looks like in practice.
