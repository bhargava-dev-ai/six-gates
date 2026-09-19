# Evals

```
set-v1.jsonl        the frozen set. One case per line. Never edited after freezing.
set-v1.sha256       its hash, written once by `freeze.py`.
runs/               one JSON record per run, named <date>_<model>_<prompt-hash>.json
```

A new set is a new version: `set-v2.jsonl` with its own hash. Old runs stay, so promotions remain reconstructible.

Case format:

```json
{"id": "c-0001", "category": "<category>", "input": {...}, "expected": {"decision": "<value>", "escalate": false}}
```

Run with `python reference/evals/run_eval.py --agent agents/<name>` from the repository root.
