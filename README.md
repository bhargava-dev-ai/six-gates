# The Six Gates

**A practitioner method for deciding, bounding, and operating AI agents.**
Six questions, asked in a fixed order, each one a gate: you do not proceed until you pass.

| | Gate | The question | Signed by |
|---|---|---|---|
| I | **Justify** | Should this be an agent at all? | requester + architect |
| II | **Grade** | How much can this thing hurt us? | risk owner |
| III | **Limit** | Who is allowed to write what? | security |
| IV | **Build** | What is the smallest supervised loop that could work? | engineering lead |
| V | **Prove** | What evidence buys this thing its freedom? | eval owner |
| VI | **Run** | Who maintains the system that maintains itself? | operations |

Any team can run all six in a one-hour session with a whiteboard. Each gate leaves a one-page artifact. A gate that leaves no artifact was not passed. It was waved.

## Start here

- **Follow the method as it develops**: [The Six Gates newsletter](https://www.linkedin.com/newsletters/7507085771422457856/), one gate and one case every two weeks, with the pushback and what changed because of it.
- **Read the method** in ten minutes: [`docs/The-Six-Gates.pdf`](docs/The-Six-Gates.pdf) (14 slides).
- **Use the templates**: copy [`templates/agent/`](templates/agent/) into your repository as `agents/<your-agent>/` and fill in the six gate files during the session.
- **Enforce Gate III in code**: [`reference/boundary/`](reference/boundary/) is a dependency-light tool boundary that reads the pens from `tools/catalog.yaml` and enforces them at runtime.
- **Pass Gate V with evidence**: [`reference/evals/`](reference/evals/) freezes an eval set, runs it, and writes a run record with the model, prompt, and catalog hashes.
- **See a finished example**: [`examples/expense-triage/`](examples/expense-triage/) is the worked example from the guide with all six artifacts filled in.

## The command

```bash
git clone https://github.com/bhargava-dev-ai/six-gates && cd six-gates && pip install -e .

sixgates init  agents/my-agent      # scaffold the folder: six gate templates, config, catalog, ledger
sixgates check agents/my-agent      # every gate signed? every argument has a pen? set frozen? owner named?
sixgates badge agents/my-agent      # README badge from config.yaml: tier, levels, gated or not
```

`check` reads files only. It exits non-zero when a gate is not passed, so it belongs in CI next to your tests. Run it on the worked example to see a passing report:

```
six gates check · examples/expense-triage · tier 2

  ✓ I   Justify  PASS
  ✓ II  Grade    PASS
  ✓ III Limit    PASS
  ✓ IV  Build    PASS
  ✓ V   Prove    PASS
  ✓ VI  Run      PASS

passed: 0 failing check(s), 0 warning(s)
```

[![Six Gates](docs/six-gates-badge.svg)](https://github.com/bhargava-dev-ai/six-gates)

## For the team running the session

*Running the Six Gates* is the 39-page implementation guide: the one-hour run sheet, who signs each gate and what they are signing for, pass criteria, fill-in templates, the promotion path, the ledger layout, a worked example with all six pages filled in, and a glossary. It goes to newsletter subscribers. Comment "guide" under any edition of [the newsletter](https://www.linkedin.com/newsletters/7507085771422457856/), or message the author on LinkedIn. The method's home page is [bhargava-dev-ai.github.io/six-gates](https://bhargava-dev-ai.github.io/six-gates/).

## Run the session in one hour

```
0:00  Read the request aloud, exactly as written. No discussion.
0:03  Gate I    Justify   → the completed sentence, or stop and build a validator
0:12  Gate II   Grade     → the worst-day paragraph and a tier
0:21  Gate III  Limit     → the tool catalog, every argument labelled with a pen
0:31  Gate IV   Build     → one agent, one checkpoint, the cascade, the escalation path
0:40  Gate V    Prove     → frozen set, baseline, thresholds written before any run
0:49  Gate VI   Run       → a name on the pager, the ledger, a date for the off-switch test
0:57  Decision  Proceed at Level 0 for every tool, or stop.
```

Three rules: gates are passed in order; a gate is passed when its artifact is signed, not when the room nods; failing a gate is a good outcome.

## The three ideas underneath

- **The Rubric Test** (Gate I). If you can write the checklist for judging the output, build a workflow or a validator, not an agent.
- **The four-tier ladder** (Gate II). Tier 1 internal productivity, Tier 2 analyst augmentation, Tier 3 operational copilot, Tier 4 customer-facing action. Grade by the worst day. Start low. Earn the climb.
- **The three pens** (Gate III). Every tool argument is written by the application, the model, or a human. Label each one. Enforce it at the tool boundary, deterministically. Prompts request; boundaries enforce.

## Repository layout

```
docs/                    the method (slides), the home page, the book outline
templates/agent/         copy this folder per agent: six gate templates, config, catalog, ledger
reference/boundary/      Gate III enforced in code: catalog-driven tool boundary + tests
reference/evals/         Gate V made reproducible: freeze, run, record
examples/expense-triage/ the worked example, all six artifacts filled in
.github/workflows/       CI that re-runs the eval when prompts or tools change
```

## Where the method is going

[`docs/book-outline.md`](docs/book-outline.md) is the chapter plan for the book the guide grows into. Cases are what it needs; see Contributing.

## Using this in your organisation

The gates are a team-level, one-hour walk through the terrain that NIST's AI Risk Management Framework and ISO/IEC 42001 cover at organisation level. The six artifacts are the evidence those frameworks ask for, produced as a by-product of deciding rather than as a separate compliance exercise. See the "Small teams and large ones" section of the guide.

## Contributing

Case studies are the most valuable contribution. If you ran the gates on a real request, open an issue titled `Case: <agent>` with two paragraphs: what the request was, which gate it died at or passed, and what changed. Corrections and template improvements are welcome as pull requests. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Citing

If the method helped you, cite it. A [`CITATION.cff`](CITATION.cff) is included; GitHub renders a "Cite this repository" button from it.

> Bhargava P. *The Six Gates: A practitioner method for deciding, bounding, and operating AI agents.* Version 1.0, September 2026.

## License

Documents, templates, and diagrams: [CC BY 4.0](LICENSE-docs). Share freely, with attribution.
Code in `reference/` and `examples/`: [MIT](LICENSE).

---

*The gates protect each other.*
