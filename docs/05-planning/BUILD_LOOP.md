# The build loop (started 22 Sep 2026)

The owner asked for the whole product to be built while they are away, with a review after every use case whose findings are fixed before the next one starts. This page is the standing plan for that loop; `CHANGELOG.md` carries the dated log.

## The order of work

| Step | Use case | What lands | Review |
|------|----------|------------|--------|
| 1 | UC2 Web app and report (v0.2.0) | US-043 word-aligned diff and page views (report schema v2), US-045 demo script and posts as drafts | Sonnet review of the web app, the report and the API, then fixes |
| 2 | UC3 Benchmark and leaderboard (v0.3.0) | corpus index, benign corpus tooling, splits and leakage audit, `paperglass bench`, baselines, `BENCHMARK.md`, dataset card, `results/` | Sonnet review of the harness and the numbers, then fixes |
| 3 | UC4 Pipeline guard and sanitise (v0.4.0) | HTML and Markdown inputs, subtractive `clean()` with fidelity and Policy, LangChain, LlamaIndex and Docling adapters, repository docs scan with pre-commit hook and GitHub Action, MCP receipt gate, API keys and rate limits, metrics and dashboard | Sonnet review of the adapters, security and the sanitiser, then fixes |
| 4 | UC5 Red kit and breadth (v0.5.0) | Red Kit generator, PPTX, images and scans, glyph arbiter, stable technique ids with disclosure, benchmark v2 | Sonnet review of coverage and false positives, then fixes |
| 5 | E6 Community and release (v1.0.0) | security review and fuzzing pass, docs site, good first issues, announcements as drafts | Sonnet cold read of the whole repository, then fixes |

Within a use case, stories go in board order; a story that needs a design decision the owner has not made is built to the decided design (`docs/04-report-design/DESIGN_DIRECTION.md`) or, if none applies, skipped with a note.

## The review ritual (after every use case)

1. Launch one review agent (Sonnet) with a read-only brief: the use case's stories, the Definition of Done, the code, tests, docs and the live development URL. It writes `docs/12-reviews/REVIEW_UC<n>.md`: findings ranked by severity, each with a file and line, a failure scenario and a proposed fix.
2. The next iteration starts by fixing every finding marked high or medium (one branch, `fix/uc<n>-review`), re-running the gate and the journey, and answering each finding in the review file (fixed, or why not).
3. Low findings become good-first-issues after launch, or are fixed when the file is next touched.

## What the loop never does on its own

Merge into `main`, tag, publish to PyPI or GHCR as a release, deploy production, spend money, add a story to the board, or change the product contract in `CLAUDE.md`. Each of those waits for the owner; the handover in `CHANGELOG.md` lists what is waiting.

## Log

- 22 Sep 2026: loop started after US-037. UC2 has US-043 and US-045 left that the loop can build; US-042 (the v0.2.0 tag and PyPI) waits for the owner.
- 22 Sep 2026: US-043 done (schema v2, the diff). US-045 drafted as far as the loop can (documents, shot list, posts); the recording and the posting wait for the owner. UC2 review agent launched.
