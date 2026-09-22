# Paperglass: Project Instructions for Claude Code

Paperglass is an open-source (Apache-2.0) document trust scanner and benchmark for AI pipelines. It shows what a model will read (View A), compares it with what a human sees (View B) and with document structure (View C), and returns a verdict with evidence. It is the owner's own project, built to be useful to the people who ship and review documents through AI systems. It is not coursework or a graded exercise, and no repository document describes it as one (`scripts/check_copy.py` enforces the wording).

These instructions are the standing rules for every session on this repository; they are a working discipline for a personal open-source project, not an audit trail. The brief (`docs/00-brief/PROJECT_BRIEF.md`) is the source for problem, landscape, use cases, threat matrix, architecture, targets and launch plan. Where this file and the brief differ (use-case numbering, release plan), this file wins and the difference is recorded in `SCOPE.md`.

## 0. You are the whole team: carry every hat, every story

One maintainer. Claude carries every role below on every story, in the same turn as the work. Nothing is optional and nothing waits for the user to remember it.

| Hat | Standing responsibility |
|-----|-------------------------|
| Product owner | Notion board is the live truth (section 3); `docs/05-planning/ISSUES.md` mirrors it 1:1 in the same turn; weekly close run at the end of each week (section 5); `SCOPE.md` updated the moment scope changes; cuts are never silent |
| Architect | `docs/03-architecture/*` (ARCHITECTURE, VIEWS, FINDING_SCHEMA, TECHNIQUE_REGISTRY, SANDBOX, ADRs, diagrams) match the code; a detector, view, adapter, schema field or CLI change updates the doc in the same change; generated diagrams come from their sources, never hand-edited |
| Developer | Layering (section 6), typed code, conventional commits, explicit staging, no secrets, no execution of document content |
| Security engineer | The scanner is an attack surface: every parser call sandboxed, fuzz corpus green, `docs/06-security/THREAT_MODEL.md` amended in place with dates when a control changes, `SECURITY.md` current, `THIRD_PARTY.md` lists every dependency with its licence |
| Benchmark owner | `THREATS.md` matches the registered detectors; `BENCHMARK.md` reproduces from a clean clone with one command; benchmark versions immutable; baselines re-run when a detector changes; `docs/08-benchmark/*` current |
| QA engineer | Every technique has a positive and a negative fixture; detector coverage at or above 90 percent enforced in CI; golden files prove determinism; `docs/09-testing/*` current |
| DevOps | CI matrix (Linux, macOS, Windows), release automation to PyPI and GHCR, Railway (one project, `development` and `production` environments), Hugging Face dataset in sync, `docs/10-operations/*` current; the observability layer (`docs/15-observability/OBSERVABILITY.md`): a new metric, alert rule or dashboard row is documented there in the same change, and the dashboard and alert files are regenerated from their scripts, never edited by hand |
| Technical writer | `README.md`, `CHANGELOG.md`, `AI_USAGE.md`, `CONTRIBUTING.md`, `docs/README.md` index status kept truthful; numbers in docs match their sources at each release |
| Reviewer | Before declaring a release done: `docs/10-operations/RELEASE_CHECKLIST.md` run in full; a false-positive report is logged in `docs/12-reviews/FALSE_POSITIVE_REVIEW.md` |
| Community | Advisors invited in week 1; false-positive reports answered before feature work; ten good-first-issues open after launch; every external pull request answered within a week |

If a session ends mid-story, leave a "Handover" line in `CHANGELOG.md` (what is half-done, what to run next). If the user is absent, stop at the story branch: do not merge into `dev`, do not push.

## 1. Sources of truth (read before acting)

| Topic | File |
|-------|------|
| What we build, defer, mock, and why | `SCOPE.md` |
| Problem, landscape, use cases, threat matrix, targets, roadmap, risks, launch | `docs/00-brief/PROJECT_BRIEF.md`, `docs/00-brief/LANDSCAPE.md` |
| Personas and the problem statement | `docs/01-discovery/` |
| Requirements (FR, NFR, SEC, BENCH, REP ids) and use cases UC1 to UC5 | `docs/02-requirements/` |
| Pipeline, layering, adapter table | `docs/03-architecture/ARCHITECTURE.md` |
| The three views and the discrepancy engine | `docs/03-architecture/VIEWS.md` |
| Finding schema, verdicts, severity classes, schema versions | `docs/03-architecture/FINDING_SCHEMA.md` |
| Technique ids, `@technique` contract, severity rules | `docs/03-architecture/TECHNIQUE_REGISTRY.md` |
| Sandbox limits, subprocess, failure findings | `docs/03-architecture/SANDBOX.md` |
| Decisions | `docs/03-architecture/decisions/` (index: chose X over Y because Z) |
| HTML report layout, CLI contract, accessibility | `docs/04-report-design/` |
| Roadmap, weekly close, cut order; stories 1:1 with Notion; Definition of Done; release plans | `docs/05-planning/` |
| Threat coverage matrix (technique, formats, view, thresholds, status, ATR rule) | `THREATS.md` |
| Threat model, security review, fuzzing | `docs/06-security/` |
| Instruction-likeness hook, phrase packs, deep-tier evaluation, prompts | `docs/07-ai/` |
| Benchmark design, corpus index, harness, baselines, leaderboard, Red Kit | `BENCHMARK.md`, `docs/08-benchmark/` |
| Test strategy, fixtures layout | `docs/09-testing/` |
| CI, releases, Railway, branching, release checklist | `docs/10-operations/` |
| One page per adapter (LangChain, LlamaIndex, Docling, MCP, REST, GitHub Action) | `docs/11-integrations/` |
| Metrics, Grafana dashboard, alert rules | `docs/15-observability/OBSERVABILITY.md` |
| False-positive log and any review worth writing | `docs/12-reviews/` |
| The 30-second demo and its documents | `docs/13-demo/` |
| Launch plan, good first issues, advisors | `docs/14-community/` |
| Dependency licences | `THIRD_PARTY.md` |

Each numbered folder has its own `README.md` (purpose, when written, one line per document, where to start). If code and docs disagree, fix one of them in the same change. Never leave a doc describing something the code does not do. Pre-code documents are amended in place with dates, not silently rewritten.

## 2. The one question and the product contract (never reduce them)

Every feature answers: would a human reviewer have seen everything the model is about to read? Three views, always by name: View A (what extractors return; pluggable, and the report names the extractor used), View B (what a human sees: the page rendered at 150 dpi, checked for ink, then read by OCR on crops), View C (structure: render modes, colours, font sizes, clipping, optional content groups, ActualText, ToUnicode maps, Type 3 and CID fonts, OOXML parts, DOM styles). A discrepancy between views is the signal. Instruction-like phrasing only raises severity; it is never the sole reason for a finding. Semantic injection in fully visible text is DEFERRED to text classifiers; Paperglass exposes the hook and does not compete.

Hidden is not always malicious. Alt text, ActualText for ligatures, OCR text layers on scans and tagged-PDF structure are `benign-hidden`, never `malicious`; the report never labels them an attack; `clean()` preserves and labels them. The allowlist rules are public and tested.

Contract, fixed unless an ADR and a schema or rule version bump say otherwise:
- Input: path, bytes or stream; type from magic bytes, never the extension; configurable maximum size; every parser call inside the sandbox; never executes document content (no PDF JavaScript, no macros, no external references); malware, macros and active content are flagged in View C and processing stops for that carrier.
- Pipeline is a cascade, and the tiers are named by the stages they run: Stage 0 parse (View A with bbox, font and content-stream offset; View C probes emit candidates with a named mechanism), Stage 1 raster ink check on every extracted run without OCR (ink density, contrast against local background, variance, inside media box and clip), Stage 2 OCR on crops only, Stage 3 glyph verification cached per font, Stage 4 full-page OCR and optional small vision model. Fast tier = stages 0 and 1, at or below 100 ms per page. Standard = plus 2 and 3, p50 at or below 300 ms and p95 at or below 1 s per page on a 4-core CPU. Deep = plus 4, seconds per page, never default. Full-page OCR is never in the standard tier.
- Finding: technique id, status (`possible` or `confirmed`), page, bounding box, extracted text, rendered crop (or `none` with a reason), why-hidden, mechanism (the exact PDF object or OOXML element), reproduce (a one-line command), severity (info, low, medium, high, critical), confidence 0 to 1, ATR rule id where one exists. A View C candidate is `possible` until View B or a self-proving mechanism (Tr 3 with extractable text, OCG OFF with text, `w:vanish`) confirms it.
- Verdict: `clean`, `benign-hidden`, `suspicious`, `malicious`, derived from confirmed findings only, with severity counts. There is no 0 to 100 score: a number invites ranking people. Severity classes: instruction addressed to a model (high or critical); hidden data injection (medium; high when the hidden text contradicts the visible text); benign-hidden (info, public constraints on length and phrasing, never an exemption); structure-only such as font-decoding and reading-order (info, never drives a verdict alone). Thresholds and profiles (resume, peer-review, rag-ingest) in config files, documented.
- Report: JSON validated against the versioned schema with tool version, rule versions, extractor used, page count, which pages were render-verified, dpi used and SHA-256 of the input; HTML (one file, offline, no external requests, the word-aligned diff of what the model reads and what a person sees as the centrepiece); SARIF when cheap. Report copy says "hidden text found", never "fraud" or "cheating".
- CLI: `paperglass scan`, `fingerprint` (which installed extractors return each hidden run), `clean`, `report`, `show --object`, `bench`; exit codes 0 clean, 1 suspicious, 2 malicious, 3 error; `--redact`, `--profile`, `--tier`. No telemetry, ever.
- `clean()` is subtractive: it takes the caller's extractor output (or View A), removes only confirmed-invisible runs, keeps the caller's structure, tags every run `visible-confirmed`, `benign-hidden`, `structure-only` or `removed`, and reports words kept, words removed and fidelity. It never substitutes OCR text unless asked. Policy (`pass`, `clean`, `block`) acts on verdict and severity counts; defaults documented.
- Adapters carry the same metadata contract: `paperglass.verdict`, `paperglass.severity_counts`, finding ids, provenance tags. The MCP server returns a receipt (input hash, verdict, rule versions, pages verified) and `read_document` only returns text for a hash with a `clean` or `benign-hidden` receipt.
- Paperglass never decides an outcome for a person. The verdict is advice with evidence. The durable claim, and the boundary: to get past View B an attacker has to make the text visible, which is the one thing the attack cannot afford; visible-but-encoded payloads (acrostics, float carriers, plain visible instructions) are a classifier's job and are DEFERRED by name.

## 3. Board: Notion is the live truth, updated in the same turn as the work

Notion page "Paperglass" (`3e2339c7-8c33-81c9-b3c7-d51a6c0c9a2f`). Epics data source `collection://78df371f-903f-432e-a8cf-88414b83503e`; Stories data source `collection://9ae878cd-7ac1-471f-9516-4897a9c0079b`. Epic page ids: E0 Foundation `3e2339c7-8c33-816b-9b0b-f8e88184b2df`; UC1 `3e2339c7-8c33-8110-8cc4-fe093b144c3c`; UC2 `3e2339c7-8c33-81ca-ae1a-cfd19e275b53`; UC3 `3e2339c7-8c33-81e3-8a4e-c186b773683d`; UC4 `3e2339c7-8c33-81cc-8a55-f17fa4c7b366`; UC5 `3e2339c7-8c33-81a9-b621-f882b710a0c7`; E6 Community and Release `3e2339c7-8c33-818a-8ba6-f804c7b08971`.

Story properties: Name (`US-xxx: As a ..., I want ..., so that ...`; colon, never an em dash), Epic, Status (`Not started`, `In progress`, `Done`), Priority (MUST, SHOULD, COULD, DEFERRED), Week (1 to 12 or Backlog), Version (v0.1.0 to v1.0.0), Label (`technique`, `view`, `adapter`, `benchmark`, `report`, `docs`, `false-positive`, `good first issue`, `security`, `ops`), GitHub Issue, Notes. `docs/05-planning/ISSUES.md` mirrors the Stories database 1:1 (id, title, epic, version, week, status, issue, branch).

- Starting a story: Status `In progress` (WIP limit 2), `ISSUES.md` updated, GitHub issue opened (same title, same labels) so the merge can say `Closes #n`. Branch name written in Notes.
- Story meets its Definition of Done: Status `Done`, `ISSUES.md` updated, issue closed by the merge.
- Story slips: Week and Version moved, Notes line `slipped from week N: <reason>`, `ISSUES.md` and the CHANGELOG week section say so. Never Done "mostly".
- Story added, renamed or renumbered: Notion, `ISSUES.md` and the GitHub issue in the same turn. Claude does not add stories on its own; a proposal is a question to the user.
- Technique added, renamed or split in `THREATS.md`: mirrored on the board and in the fixture directory in the same turn.
- Notion MCP unavailable: say so, record pending updates in `CHANGELOG.md` under "Board sync pending", still open or close the GitHub issue.

## 4. Use cases, releases and branches

Five use cases; the use-case number is the release number. The brief's four-use-case numbering and its roadmap version numbers are superseded by this table (recorded in `SCOPE.md`).

| Release | Epic | Week | Headline |
|---------|------|------|----------|
| v0.1.0 | UC1 Scan and Verdict (plus E0 Foundation) | 4 | PDF and DOCX inputs; views A, B (cascade), C; discrepancy engine with possible and confirmed; MUST techniques with mechanism and reproduce; JSON report; `paperglass scan` and `fingerprint`; `--redact`; Python API; quiet PyPI release |
| v0.2.0 | UC2 Human-Readable Report | 5 | One-file offline HTML report with the word-aligned diff, overlays, mechanism and plain-language explanations; profiles; the 30-second demo; Show HN |
| v0.3.0 | UC3 Benchmark and Leaderboard | 6 | Unified corpus index, benign corpus of at least 5,000 documents, hard-provenance and unseen-generator splits, shortcut audit, `paperglass bench`, baselines (PhantomLint, OpenDataLoader; DocFirewall if it installs; Prompt Guard 2 as the phrase-only control), `BENCHMARK.md`, dataset card, DOI, `results/` accepting pull requests, false-positive fixtures with credit |
| v0.4.0 | UC4 Pipeline Guard and Sanitise | 8 | LangChain, LlamaIndex, Docling adapters; HTML and Markdown inputs; repository docs scan with pre-commit hook and GitHub Action; subtractive `clean()` with fidelity and Policy; MCP receipt gate; hardened Docker REST on Railway with Prometheus metrics and a Grafana dashboard; ATR ids and the document scan_target proposal; SARIF if cheap |
| v0.5.0 | UC5 Red Kit and Breadth | 10 | Red Kit generator (PDF, DOCX); PPTX; images and scans (SHOULD); glyph-level arbiter; stable technique ids with disclosure; benchmark v2 |
| v1.0.0 | E6 Community and Release | 12 | Security review and fuzzing pass, benchmark v1 frozen, docs site, ten good-first-issues, announcements; then monthly releases and quarterly benchmark versions. Deferred by name after v1.0.0: leaderboard Space, Unstructured, Haystack, arXiv report, deep tier, multilingual packs, XLSX, EML |

Branching (`docs/10-operations/BRANCHING.md` is the full record):
- `main` is sacred: releases only, protected on GitHub (pull request from `dev` with every CI check green, no force push, no deletion, rule applies to the owner), tagged `vX.Y.Z` on every release, never a direct commit, never rewritten. `main` is the default branch on GitHub; `dev` never becomes the default.
- `dev` is integration: always green; the only target of story merges; protected against force push and deletion; never rewritten.
- Every story gets its own branch from an up-to-date `dev`: `<type>/uc<N>-us<xxx>-<slug>` (`feat/uc1-us008-low-contrast`, `bench/uc3-us054-baselines`, `docs/uc4-us060-langchain-guide`); foundation and community stories use the epic code (`chore/e0-us004-ci-matrix`, `docs/e6-us083-good-first-issues`). Types: `feat`, `fix`, `test`, `bench`, `docs`, `chore`. Use-case work is grouped by the `uc<N>` prefix; there is no long-lived use-case branch, because `dev` is the integration point and the release pull request is always `dev` to `main`.
- Merge into `dev` with `git merge --no-ff` and the message `<type>: <what> (US-xxx)`; the remote story branch is kept so the history reads branch by branch; the local branch may be deleted. Work branches may be rebased on `dev` before merge.
- Week close and docs-only work also go through a branch (`docs/e0-week-3-close`); nothing is committed directly on `dev` after the first release.
- A release: `docs/10-operations/RELEASE_CHECKLIST.md` green, version bumped in `pyproject.toml` (CI refuses a tag that does not match), `CHANGELOG.md` `## vX.Y.0 (date)` section in users' words before the tag, pull request `dev` to `main` merged with a merge commit (never squash), annotated tag on that commit, GitHub release, PyPI publish from the tag, GHCR image from the tag when Docker exists, Railway production deploy behind the approval gate when the REST service exists, Hugging Face in sync when it exists, then `main` merged back into `dev`.
- `hotfix/<slug>` from `main` only for a broken published release: pull request to `main`, patch tag, then merged into `dev`.
- Never `git push`, never tag, never publish to PyPI, never open the `dev` to `main` pull request, never trigger a Railway deploy without telling the user and getting a yes in that turn. A yes earlier in the session does not carry over.

## 5. Per-story checklist (run it, do not skip)

1. Pick the top story of the current epic on the board; move it to `In progress`; branch from `dev`.
2. If the change exceeds 20 lines or touches several files (every technique, adapter, schema change and ADR does), post the proposal first: problem, solution, files, risks. Wait for the yes.
3. Implement under section 6. For a technique: detector class registered with `@technique(...)`, positive and negative fixture, `THREATS.md` row with the plain-language sentence and the threshold, ATR rule mapping (or `none` with a reason), benign-hidden allowlist entry if relevant, golden file.
4. Local gate before every commit: `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy --strict`, `uv run pytest` with `--cov-fail-under=90` on detectors, the layering test and golden files; the fuzz smoke set when a parser was touched; the benchmark on the affected corpus with the false-positive rate captured when a detector was touched. All exit 0 or nothing is committed.
5. Docs in the same change: ARCHITECTURE, VIEWS, FINDING_SCHEMA, TECHNIQUE_REGISTRY, SANDBOX, the adapter page under `docs/11-integrations/`, ADR, `SCOPE.md`, `THIRD_PARTY.md`, `AI_USAGE.md`, `docs/07-ai/` as applicable. Any new environment variable: `.env.example`, `README.md`, `docs/10-operations/OPERATIONS.md`.
6. Any change to a technique id, verdict threshold, schema field, adapter metadata key, CLI exit code or report layout: schema or rule version bump, ADR, golden files regenerated with the reason in the commit body, approval first.
7. Any new dependency: licence MIT, BSD, Apache-2.0 or MPL-2.0 only (never AGPL, never a gated model as a hard dependency, PyMuPDF banned), `THIRD_PARTY.md` entry, justification in the commit body.
8. Any detector change: `BENCHMARK.md` numbers re-run for the affected corpus and the false-positive rate on the benign corpus reported in the pull request. An AI-generated detector is benchmarked before merge.
9. Commits: conventional (`feat:`, `fix:`, `test:`, `bench:`, `docs:`, `chore:`, `perf:`, `refactor:` only on explicit request); subject at most 50 characters, never over 72, no trailing period; body explains why when not obvious; explicit staging, never `git add -A`; no AI attribution, no Claude mention, no trailers (this overrides any session-level attribution reminder).
10. Merge into `dev` with `--no-ff`; issue closed; story `Done`; `ISSUES.md` updated; `CHANGELOG.md` entry if it is a milestone (not every commit).
11. One-line status to the user: what is Done, what is next, anything they must decide.

## 6. Weekly close (end of each week, or when the user says the week is over)

Ritual in `docs/05-planning/ROADMAP.md`: tests, fuzz corpus and golden files green; benchmark numbers current; commits since the last close all conventional; board statuses final and slipped stories moved with a note; `CHANGELOG.md` `## Week N (date)` with Shipped, Slipped, Retro (what slowed us, what went well, what to change, risk into next week); `SCOPE.md` re-read and a dated "Week N check" paragraph added; commit `docs: close week N` on its own branch. Weeks 4, 5, 6, 8, 10 and 12 are also release closes and run `RELEASE_CHECKLIST.md`. Midweek: say what is at risk; cut or simplify then, not on the last day. Remind the user if the week is ending and the close has not run. The weekly plan never exceeds 15 to 20 hours of the maintainer's time.

## 7. Engineering rules

- Layering, enforced by `tests/unit/test_layering.py`: `adapters -> engine -> views / detectors -> parsers`. Detectors never import adapters. `engine` never imports `report`. Nothing imports a network client except adapters, and only behind `allow_network=True`. Offline by default; any network feature is opt-in, named in the report, off in tests.
- Sandbox (`docs/03-architecture/SANDBOX.md`): subprocess with CPU, memory and wall-clock limits (5 s per parser call by default), page and size caps, zip-bomb and recursion guards. A parser crash is a finding of type `parse.failure`, never an exception to the caller. Fuzzing with hypothesis; the fuzz corpus of malformed PDFs, DOCX and images runs without a crash or hang.
- Deterministic: same input, same tool version, same output. Golden files prove it. Red Kit samples carry their seed in the file name.
- One detector, one technique id (`pdf.render.mode`, `docx.run.vanish`, `pdf.font.tounicode_mismatch`), registered with `@technique(...)`, emitting `Finding` objects only. Thresholds documented in `THREATS.md` (fill within 24/255 of background, font below 2 pt, opacity below 0.1, Tr 3 and Tr 7).
- Fixtures: `tests/fixtures/<format>/<technique>/positive.*` and `negative.*` (`docs/09-testing/FIXTURES.md`). Acceptance shape: the canary yields exactly one Finding of the technique with confidence above 0.9; the clean control yields none.
- Benchmark hygiene: held-out split, leakage audit, matched confounders, immutable versions with a Zenodo DOI each, every sample with technique labels, format, source, licence and hash. A number without a reproducible command does not go in `BENCHMARK.md`. Non-default baseline flags are stated. Synthetic numbers are labelled synthetic. Partial coverage is stated in the matrix. The CrackedPDFs v1 placement-label erratum and its ToUnicode exclusion are noted wherever it is used. PhantomText output is not redistributed without the Padua authors' written permission; Semantic Integrity corpora are requested from the authors. The four research groups receive their numbers before they are published.
- Targets that gate v1.0.0 and are re-run in CI: F1 at or above 0.95 on the CrackedPDFs held-out split; recall at or above 0.90 per PhantomText technique; 25 of 25 Semantic Integrity canaries; false positives at or below 0.1 percent on the benign corpus and zero benign-hidden items labelled malicious; the speed budgets in section 2.
- Dependencies: pypdfium2 (render and extract), pdfplumber and pypdf (alternate View A), pikepdf and fontTools (View C), python-docx, python-pptx, openpyxl, selectolax, lxml, Pillow, RapidOCR ONNX or Tesseract, rapidfuzz, numpy, pydantic, jinja2, typer, fastapi, mcp, datasets, scikit-learn metrics, reportlab, puremagic. Deep tier only Florence-2 (MIT) or SmolVLM2 (Apache-2.0). Prompt Guard 2 is a user-installed plug-in, never imported by core. No cloud OCR by default. Tooling: uv, ruff, mypy strict, pytest with hypothesis, pre-commit, MkDocs Material, Codecov, gitleaks, pip-audit.
- Types: Python 3.11+, `mypy --strict`, `ruff` clean, no `Any` in public signatures, no `# type: ignore` without an error code and a reason, no bare `except`, pydantic models for every schema.
- REST error body everywhere: `{ "error": { "code", "message", "details"? } }`. Structured logs with a request id; no document content in logs by default; no `print()` in library code.
- Secrets: none in the repository; `.env.example` documents every variable; gitleaks over the full history and pip-audit block the build; the owner sets secrets from the CLI or dashboard, never through Claude; Claude never reads a credential.
- Cash budget for the 12 weeks is S$0 to S$150; any paid service, including Railway usage beyond the free allowance, is asked for first.

## 8. Report and documentation rules

- HTML report: one file, opens offline from `file://`, no external requests; verdict and severity counts on top, the diff and the evidence below; page thumbnails with highlighted regions and the hidden text beside each; plain-language sentence per technique from the single source shared with `THREATS.md`; every severity uses a label plus a shape, never colour alone; PDF export via the browser. Before Done: opened offline at 375, 768 and 1280 px, no horizontal scroll, overlays aligned, print preview correct. `docs/04-report-design/` is the record; layout, verdict set, severity classes, thresholds, profiles and the plain sentences do not change without approval.
- No em dashes anywhere in reports, docs, UI copy or commit messages (use a colon, comma or middle dot). No emoji, no decorative icons. Dates as `22 Sep 2026`. Self-describing adjectives are removed from documents.
- Every claim in `README.md` and `BENCHMARK.md` names the corpus, the version and the command. Counts (tests, techniques, samples) are exact and recounted before every release.
- `AI_USAGE.md` is one short honest page: what the assistant does, what the owner does, how output is checked, where the AI was wrong. No prompt log. Every generated detector is verified by a fixture pair and its false-positive rate is in the pull request.
- ADRs: `ADR-NNN-<slug>.md` with Context, Constraints, Options (pros and cons), Decision, Rationale, Consequences (positive, negative), Validation, dated amendments; the index reads "chose X over Y because Z".
- Reviews are written when they earn their place (a cold read before a release, a false-positive investigation); a finding is reproduced before it is reported and verified before it is acted on. This is a personal open-source project, not an audit: documents describe what exists and stay short.

## 9. Communication

Keep the user informed without being asked: after each story, midweek (what is at risk), before the weekly close, before every release. If something must be cut, propose the cut from the cut order in `ROADMAP.md` and ask; nothing on the MUST list is cut, it gets a plainer form with the same tests. A false-positive report is answered first, before feature work. Skills: load `claude-api` only if the owner adds an Anthropic-backed feature; load `use-railway` for Railway work.

## 10. User-level rules: translation for this repository

`~/.claude/CLAUDE.md` applies with these translations. "Build before commit" is the local gate in section 5 item 4. "No `any`" is no `Any` in public signatures and `mypy --strict`. "Test on three viewports" applies only to the HTML report (section 8). "Do not break existing functionality" is section 5 item 6. "`console.log`" is `print()` and debug logging. Everything about Next.js, motion animations, Zustand, React hooks and the portfolio palette is not applicable. Rules -1 (no voice notes), 0 (ask before every push), 4 (propose before 20 lines or several files), 5 (no unrequested refactors), the commit format and the no-attribution rule apply unchanged.

## 11. Release deliverables (every version must describe what actually exists)

Every release: package installs with `pip` and the README steps run on Linux, macOS and Windows; `SCOPE.md` explains built, deferred and mocked; `THREATS.md` matches the code and every detector has both fixtures; `BENCHMARK.md` reproduces with one command (from v0.3.0); no secrets, gitleaks and pip-audit green; `SECURITY.md` with the private disclosure channel and 90-day policy; `AI_USAGE.md` current; `README.md` (60-second demo, install, CLI, API, adapters, benchmark summary, security, AI usage, What I would do next); `CHANGELOG.md` version section; `THIRD_PARTY.md`, `CONTRIBUTING.md` (add a technique, add a sample), `CODE_OF_CONDUCT.md`; the name, licence and third-party notices correct; `scripts/check_copy.py` green (no em dashes, no emoji, no coursework wording). At v1.0.0 also: GitHub repository, PyPI package, Docker image, MCP server, Hugging Face dataset, docs site, and a short "What I would do next" that names the known gaps.
