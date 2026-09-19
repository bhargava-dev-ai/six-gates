# Changelog

## 1.0.0 · 2026-09-19

- `sixgates` command: `init` scaffolds an agent folder from the templates, `check` verifies the ledger gate by gate and exits non-zero when a gate is not passed, `badge` writes a README badge from `config.yaml`.
- Home page at bhargava-dev-ai.github.io/six-gates with the one-page summary card and how to get the implementation guide, which is distributed to newsletter subscribers.
- Book outline in `docs/book-outline.md`.

## 1.0.0-rc · 2026-09-18

- The Six Gates method published as a 14-slide document.
- *Running the Six Gates*, the implementation guide, written. Distributed to newsletter subscribers rather than shipped in this repository.
- Templates: six gate artifacts, agent README, config, tool catalog, ledger layout.
- Reference tool boundary enforcing the three pens from `tools/catalog.yaml`, with tests.
- Reference eval harness: freeze a set, run it, record model, prompt, and catalog hashes.
- Worked example: expense-report triage, all six artifacts filled in.
