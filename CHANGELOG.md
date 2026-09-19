# Changelog

## 1.0.0 · 2026-09-19

- `sixgates` command: `init` scaffolds an agent folder from the templates, `check` verifies the ledger gate by gate and exits non-zero when a gate is not passed, `badge` writes a README badge from `config.yaml`.
- Implementation guide expanded with a plain-language layer: "Read this first", the five-minute version, reading paths by role, "In plain words" and "Picture this" for every gate, beginner questions, a one-page summary card, and a glossary.
- Book outline in `docs/book-outline.md`.

## 1.0.0-rc · 2026-09-18

- The Six Gates method published as a 14-slide document.
- *Running the Six Gates* implementation guide: one-hour session, run sheets, pass criteria, artifact templates, promotion path, change triggers, ledger layout, worked example, notes and further reading.
- Templates: six gate artifacts, agent README, config, tool catalog, ledger layout.
- Reference tool boundary enforcing the three pens from `tools/catalog.yaml`, with tests.
- Reference eval harness: freeze a set, run it, record model, prompt, and catalog hashes.
- Worked example: expense-report triage, all six artifacts filled in.
