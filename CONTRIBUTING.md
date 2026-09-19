# Contributing

## Case studies

The most useful thing you can add is evidence that the method was run on a real request.

Open an issue titled `Case: <agent name or domain>` with:

1. The request as it was asked, one paragraph.
2. Which gate it died at, or the tier and level it reached.
3. What changed because of the session: the validator that got built instead, the argument that moved from model pen to human pen, the eval that failed.

Keep it to two or three paragraphs. Anonymise freely. Cases are added to `docs/cases/` with attribution unless you ask otherwise.

## Corrections and improvements

- Template wording, pass criteria, and run-sheet timings: open a pull request against `templates/` with a one-line reason.
- Reference code: pull requests must keep `pytest` green and add a test for any new behaviour.
- The method itself (the six gates, their order, the ladder, the pens) changes only with a version bump and a changelog entry. Open an issue first.

## Versioning

The method is versioned like software. Patch versions fix wording. Minor versions change templates or requirements tables. A major version would change a gate, and there is no plan for one.
