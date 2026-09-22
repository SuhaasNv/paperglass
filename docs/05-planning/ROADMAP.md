# Roadmap: 12 weeks, six releases

Start: week 1 begins Monday 22 Sep 2026 (planning done the same day). One maintainer, 15 to 20 hours a week, AI-assisted under `CLAUDE.md`. The use-case number is the release number. Stories: `ISSUES.md`. Every week ends with the close ritual below; release weeks also run `../10-operations/RELEASE_CHECKLIST.md`.

## Weeks

| Week | Dates (2026) | Serves | Goal | Stories | Load |
|------|--------------|--------|------|---------|------|
| 1 | 22 to 28 Sep | v0.1.0 | Skeleton, schema, sandbox, CI, governance, View A, advisors invited | US-000 to US-006, US-022 | 8, on budget |
| 2 | 29 Sep to 5 Oct | v0.1.0 | View C and ten PDF techniques, fixtures, fuzz, verdict rules, mechanism fields | US-007 to US-021, US-024 | 16, over budget: the four hardest (US-014, US-015, US-016, US-017) are the first to slip to week 3 |
| 3 | 6 to 12 Oct | v0.1.0 | View B cascade, discrepancy engine, covered text, font fallbacks, DOCX, fingerprint | US-023, US-030 to US-034, plus week 2 slips | 6 plus slips |
| 4 | 13 to 19 Oct | v0.1.0 | CLI, instruction hook, redact, quiet PyPI release | US-025, US-036, US-038, US-039 | 4, release week |
| 5 | 20 to 26 Oct | v0.2.0 | The web app: backend with Postgres, React shell, results screen with the diff, profiles, techniques page, images and Railway, CI for the frontend and the journey, demo, Show HN | US-037, US-041 to US-049 | 13, release week; the corpus stories US-050 and US-051 move to week 6 |
| 6 | 27 Oct to 2 Nov | v0.3.0 | Corpus index and benign corpus, harness, splits, baselines, BENCHMARK.md, results/, false-positive fixtures, release and announcement | US-050 to US-059 | 9, release week; the leaderboard Space was already deferred to keep this week honest |
| 7 | 3 to 9 Nov | v0.4.0 | LangChain, LlamaIndex, Docling, GitHub Action, HTML and Markdown | US-060 to US-063, US-072 | 5 |
| 8 | 10 to 16 Nov | v0.4.0 | Subtractive clean, MCP gate, API keys and hardening, production runbook and domains, Prometheus and Grafana, docs scan and pre-commit, ATR, SARIF if cheap, release | US-040, US-064 to US-069, US-079, US-089 | 9, release week; US-089's Grafana half is the first to slip to week 9 |
| 9 | 17 to 23 Nov | v0.5.0 | PPTX, images and scans, scan hardening | US-035, US-070, US-073 | 3 (glyph arbiter research starts) |
| 10 | 24 to 30 Nov | v0.5.0 | Red Kit, glyph arbiter, reading order, disclosure ids, benchmark v2, release | US-075, US-077, US-078, US-087, US-088 | 5, release week |
| 11 | 1 to 7 Dec | v1.0.0 | Security review and fuzzing pass, docs site, benchmark v1 frozen and baselines re-run | US-080 to US-082 | 3 |
| 12 | 8 to 14 Dec | v1.0.0 | Good-first-issues, announcements, reviews, release | US-083 to US-086 | 4, release week |

Backlog (COULD and DEFERRED): US-071, US-074, US-076, US-084's arXiv part, US-090 to US-099.

## Cadence

| Event | When | Output |
|-------|------|--------|
| Week planning | Monday, 15 min | stories for the week in dependency order; WIP limit 2 |
| Midweek check | Wednesday or Thursday, 5 min | what is at risk is cut or simplified now, from the cut order; `SCOPE.md` updated if scope changes |
| Weekly close | Sunday or when the owner says the week is over | the ritual below; `CHANGELOG.md` entry |
| Release close | weeks 4, 5, 6, 8, 10, 12 | the weekly close plus `RELEASE_CHECKLIST.md`, the pull request `dev` to `main`, the tag |

## Weekly close ritual (run every time)

```
1. uv run ruff check . && uv run ruff format --check . && uv run mypy --strict && uv run pytest   (fuzz and golden included)
2. Benchmark numbers current for any detector changed this week (BENCHMARK.md or "no detector change")
3. git log since the last close: every commit conventional, every story on its own branch merged --no-ff
4. Notion: Done stories Done; unfinished stories moved to next week with Notes "slipped from week N: <reason>"; ISSUES.md regenerated
5. CHANGELOG.md: "## Week N (<dates>)" with Shipped / Slipped / Retro (what slowed us, what went well, what to change, risk into next week)
6. SCOPE.md: re-read; a dated "Week N check" paragraph; MUST/SHOULD/COULD/DEFERRED updated if anything changed
7. docs/README.md status column truthful
8. Commit on a branch docs/e0-week-N-close, merge --no-ff into dev: "docs: close week N"
```

Never mark a story Done that fails `DEFINITION_OF_DONE.md`. Remind the owner if the week is ending and the close has not run.

## Cut order (apply in this order if behind; decided up front)

1. SARIF (US-040): after v1.0.0.
2. Reading-order splits (US-077) and the HTML web-font twin: document as known gaps.
3. Images and scans (US-035, US-073): route scans to the deep tier only; document.
4. PPTX (US-070): after v1.0.0.
5. Profiles beyond `default` and `resume` (US-044): ship two, document the third.
6. Docling adapter (US-062): Docling as a View A extractor only; the pipeline step after v1.0.0.
7. `paperglass fingerprint` extractors beyond pypdfium2, pdfplumber, pypdf: the rest after v1.0.0.
8. Prompt Guard 2 baseline (US-054): report DocFirewall's or the phrase-only control once, or omit with a sentence.
9. Glyph arbiter (US-087): ship the static probes as informational and say so in `THREATS.md`; the arbiter becomes the first post-1.0 release.
10. Red Kit DOCX generator: PDF only.

Never cut: the MUST rows in `SCOPE.md` for UC1 and UC3, the fixture pair rule, the sandbox, the benchmark hygiene, the honesty rules. If the MUST list is at risk the answer is a smaller surface with the same tests, not fewer guarantees. Any week that slips two items triggers this list before it extends the calendar.

## Risks and responses

| Risk | Response |
|------|----------|
| Week 2 is overloaded | Four techniques pre-marked to slip into week 3; View C (US-007) is the only blocker (in fact the whole of v0.1.0 landed in week 1) |
| Week 5 carries the web app (13 stories) | The backend, app shell, images and CI wiring start in week 2, as soon as the design pass for the screens is scheduled; only the designed screens wait |
| Glyph arbiter harder than planned | Static probes ship informational; arbiter can slip past v1.0.0 without breaking a promise |
| Corpus permissions (Semantic Integrity by request) | Canaries rebuilt from the paper if no reply by week 3 |
| Benign corpus download size | Script downloads, never commits; a 500-document subset for CI, the full 5,000 for `BENCHMARK.md` |
| OCR dependency weight | `paperglass[ocr]` extra; fast tier has no binary dependency |
| Adapter churn | Optional extras with pinned CI; a broken adapter is marked unsupported, never blocks a release |
| Maintainer time | 15 to 20 hours a week is the plan's ceiling; the cut order is applied before the calendar moves |
| Railway cost | Free allowance expected; anything beyond is asked for first (S$0 to S$150 total budget) |
