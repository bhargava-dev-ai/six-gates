# The Six Gates: book outline

Working title: **The Six Gates: How to decide, bound, and operate AI agents that survive production**
Target: 55,000 to 65,000 words. Fourteen chapters in four parts, plus appendices.
Audience: architects, tech leads, product owners, and risk reviewers who are asked "we want to build an AI agent" and have no method to answer with. Readable by a non-engineer; the code lives in the appendices.

Status legend: **have** = exists in the guide or repo · **expand** = exists in outline form, needs depth · **collect** = needs real cases from running the gates with teams.

## Part I · Why gates

| Ch | Title | Words | Status | Contents |
|---|---|---|---|---|
| 1 | The demo culture | 4,000 | expand | Why agents got demos where clouds got a well-architected framework. The six places improvised methods fail. Moffatt v. Air Canada told as a story. What a method has to be to survive a meeting. |
| 2 | Six questions in one hour | 3,500 | have | The method at a glance. The three rules. Roles and signatures. The run sheet. Why the order matters and what each gate protects. |

## Part II · The gates

Each chapter follows the same shape: the idea in plain words, the analogy, the run sheet, the pass criteria, two or three real cases (anonymised), the ways teams wave it, the template, and the implementation notes.

| Ch | Title | Words | Status | Cases needed |
|---|---|---|---|---|
| 3 | Justify: the Rubric Test | 5,000 | expand | Two agents that became validators; one that was justified for a sliver of the work |
| 4 | Grade: the four-tier ladder | 5,000 | expand | One "just internal" tool that was Tier 4; one pilot that became production by momentum |
| 5 | Limit: the three pens | 6,000 | expand | One prompt-injection near miss; one service-account over-reach; one vendor platform with hidden arguments |
| 6 | Build: the smallest supervised loop | 5,000 | expand | One multi-agent system that could not be debugged; one approval screen that changed the outcome |
| 7 | Prove: purchasing autonomy | 6,000 | expand | One "we watched it" agent that failed after a model upgrade; one promotion earned category by category |
| 8 | Run: the ledger | 5,000 | expand | One forty-rule prompt; one off switch that did not work when pressed; one agent-authored skill that went live unreviewed |

## Part III · Running it

| Ch | Title | Words | Status | Contents |
|---|---|---|---|---|
| 9 | The session, minute by minute | 4,000 | have | Facilitation. The scribe. What to do when the room designs instead of decides. Running it remotely. Running it in twenty minutes for a small tool. |
| 10 | Evals in depth | 5,000 | expand | Building the frozen set. Sampling the weird twenty percent. Baselines. Metrics per tier. Model-as-judge and when it lies. CI integration. Demotion. |
| 11 | Operating agents | 4,000 | expand | The ledger in practice. Deletion passes that hurt. Provenance for self-improving agents. Incident response when a gate was skipped. Re-grading. |
| 12 | Gates in the organisation | 4,000 | collect | Mapping to NIST AI RMF and ISO/IEC 42001. Procurement questions for vendor platforms. Gates as the definition of ready. Reporting to a board. |

## Part IV · Cases

| Ch | Title | Words | Status | Contents |
|---|---|---|---|---|
| 13 | Six agents, six gates | 5,000 | collect | Six end-to-end walks, one per tier and domain: expense triage (have), customer service, procurement, code review, clinical or legal copilot, internal search |
| 14 | When the gates were skipped | 3,500 | collect | Post-mortems reconstructed gate by gate. Which gate was skipped, what it cost, what the artifact would have said. |

## Appendices

| | Title | Status |
|---|---|---|
| A | The six templates | have |
| B | The reference tool boundary, annotated | have |
| C | The eval harness, annotated | have |
| D | The one-page summary card | have |
| E | Glossary | have |
| F | Notes and further reading | have |

## What exists today

The implementation guide (about 11,000 words after the plain-language expansion) covers chapters 2, 9, and the appendices, and gives each of chapters 3 to 8 its skeleton: run sheet, pass criteria, template, one "picture this" scenario, and implementation notes. The repository gives appendices A to C as working files.

## What has to be collected

About twenty anonymised cases across chapters 3 to 8, 13, and 14. Each needs: the request as asked, the gate it died at or the tier and level it reached, and what changed. The CONTRIBUTING file asks for exactly this. Twenty cases at two hours each is the real cost of the book. Everything else is writing.

## How to help

The cases are the part that cannot be written alone. If you ran the gates on a real request, open an issue titled `Case: <agent or domain>` as described in CONTRIBUTING.md. Two paragraphs is enough.
