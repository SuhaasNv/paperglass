# Changelog

All notable milestones. One section per weekly close plus in-week milestones. Story ids refer to `docs/05-planning/ISSUES.md`. Release sections are written in the users' words before the tag.

## v0.2.0 (in progress): UC2 Web app and report

- US-046: `backend/`, a FastAPI service that scans an upload in memory, keeps the report 7 days under an unguessable id, scopes history to an anonymous signed cookie, and runs on PostgreSQL through Alembic; tests on SQLite and on PostgreSQL in CI.
- US-047: `frontend/`, the React app shell (upload, results with fingerprint, history, techniques, about) wired to the API as plumbing; vitest and a Playwright journey at three widths. Screens wait for the design pass.
- US-049: CI jobs Frontend and End to end.
- US-048: backend and frontend images, `compose.yaml`, the Images workflow to GHCR with smoke tests; Railway `development` (from `dev`) and `production` (from `main`) each with their own PostgreSQL, wait-for-CI on every trigger; both live on 22 Sep 2026 after pull request #24 brought `main` up to `dev` (no version tag yet: the tag and the PyPI publish follow the release checklist). The PostgreSQL driver is pg8000 (BSD-3); psycopg was LGPL.
- Fix: the sandbox tests broke on every platform after the backend tests changed the import mode; the backend tests now live in `tests/backend/`.
- US-044: profiles `resume`, `peer-review` and `rag-ingest`; every threshold and benign-hidden limit now comes from the profile file, none from code; `GET /api/v1/profiles`.
- US-041: closed; the registry already feeds THREATS.md, the report and the techniques page.
- US-037 (screens): the web app built to direction 1, "the Lens": landing at `/`, scanner at `/scan`, results with every confirmed region under the glass, history, techniques, about; self-hosted Instrument Serif, Hanken Grotesk and Geist Mono; grain, one signal colour, scroll-linked motion; Playwright checks the lens and sideways scroll at three widths. The design record is in `docs/04-report-design/DESIGN_DIRECTION.md`.
- US-043: the diff. Report schema v2 carries every page (a JPEG thumbnail, every extracted run with its box and a status: visible, hidden, benign-hidden, unverified, tied to its finding); the web results page and the HTML report put the real page under the glass with the runs overlaid and a reading-order column; invisible characters shown as code points; ADR-007.
- UC2 review (build loop): one medium and four low findings, all fixed: hourly retention sweep, clean verdict as the outlined circle, best-fit run linking, touch halo on page overlays, forwarded-IP note; regression tests for autoescaping, the clean shape, the sweep and the overlap. `docs/12-reviews/REVIEW_UC2.md`.
- US-045 (drafts): the demo documents (`scripts/make_demo_documents.py`), the shot list rewritten to the web app and the CLI, the Show HN, OWASP GenAI and docling-parse posts drafted in `docs/14-community/LAUNCH_POSTS.md`. Recording and posting wait for the owner.
- US-037 (report): the one-file HTML report, `paperglass report`, `scan --report`, and `GET /api/v1/scans/{id}/report.html` behind the results page's download link; offline, no external request, the same evidence with the regions under a pointer-following ring.

Build loop (22 Sep 2026): the owner asked for the rest of the product to be built unattended, one review agent after every use case, findings fixed before the next; the plan is `docs/05-planning/BUILD_LOOP.md`.

Handover (22 Sep 2026): the web app runs at https://frontend-development-341b.up.railway.app (dev) and https://frontend-production-ae91.up.railway.app (main). What remains in v0.2.0: US-045 demo (script and posts as drafts), the UC2 review (build loop), then US-042 release (version bump, tag, PyPI), which waits for the owner.

## v0.3.0 (in progress): UC3 Benchmark and leaderboard

- US-052: the harness. `paperglass bench fetch|run|report|verify`, any detector through the two-function adapter (`paperglass` or `module:function`), the corpus index format with a synthetic `fixtures` corpus built from the repository's own fixture pairs, metrics in plain Python (verdict recall and detection recall kept apart, per technique and per family, instruction versus data, two false-positive rates, benign-hidden mislabelled, latency), `results/` with Paperglass's own file and a CI step that refuses it if it does not reproduce. Nothing here is a headline number.
- US-050: the corpus index over the external sources: `paperglass bench fetch --corpus v1` with CrackedPDFs (Hugging Face, the paper's pinned revision and frozen test split, whole base documents sampled), PhantomLint's fixtures (GitHub, pinned commit) and PhantomText (generated when the toolkit is installed); the wildcard label for hidden text of unspecified technique; the `visible` family for payloads Paperglass defers by contract. First run on real documents: all six clean PhantomLint documents called suspicious; four false-positive causes logged in `docs/12-reviews/FALSE_POSITIVE_REVIEW.md` and fixed next.
- US-053: `paperglass bench split` (hard provenance by base document, a held-out source as the unseen generator, refuses a straddle) and `paperglass bench audit` (label-shuffle check against chance, text-only TF-IDF shortcut audit through the bench extra); results files carry metrics per split. On the fixtures corpus the shuffle collapses and the shortcut audit fires, as expected of planted sentences.

## v0.1.0 (unreleased): UC1 Scan and Verdict

What you get: `pip install paperglass`, then `paperglass scan file.pdf` (or a `.docx`, `.txt`, `.md`, or a whole directory) prints a verdict of clean, benign-hidden, suspicious or malicious, with every finding's technique in plain words, the page and region, the hidden text, the exact object that hid it, and a `paperglass show` command that prints those bytes so you can check without trusting the tool. `paperglass fingerprint` tells you which of your installed PDF extractors would hand the hidden text to a model. The Python API (`paperglass.scan`, `paperglass.fingerprint`) returns the same as typed models with a versioned JSON schema.

New: 18 detection techniques for PDF, DOCX and plain text, each with a positive and a negative fixture (`THREATS.md`); a three-view pipeline where structure finds candidates and the rendered page confirms them; a sandboxed worker with memory and time limits so a malicious file becomes a finding, not a crash; exit codes for shell pipelines; `--redact` for reports you keep; no telemetry.

Known limits: ToUnicode, ActualText and undecodable-font findings are informational until the glyph arbiter (v0.5.0); DOCX has no rendered view yet; OCR (the standard tier) needs `pip install "paperglass[ocr]"`; speed is measured on a laptop, not the 4-core Linux target; Windows enforces the wall clock but not CPU or memory caps. Nothing here decides anything about a person: the verdict is advice with evidence.

## Week 1 (22 to 28 Sep 2026)

Closed early on 22 Sep 2026 with the v0.1.0 code complete on `dev`; the release itself waits for the owner (PyPI trusted publishing, the pull request to `main`, the tag).

### Shipped

| Story | Outcome |
|-------|---------|
| US-000 to US-006 | Skeleton, schema v1 with golden files, registry and the THREATS.md contract test, sandbox and guards, CI on three operating systems (12 jobs green), governance files, View A with four PDF extractors |
| US-007 to US-018, US-024 | View C for PDF; ten detectors with fixture pairs; mechanism and reproduce on every candidate |
| US-020, US-021, US-030 to US-034 | Verdict rules and profile file, fuzz corpus, View B cascade, discrepancy engine, covered text, static font probes, DOCX views and four detectors |
| US-023, US-025, US-036, US-038 | Fingerprint, redact and no telemetry, the CLI with a long-lived sandbox worker (fast tier 18 ms p50), the instruction-likeness plug-in hook |
| US-005, US-022 (part) | Licence, security policy, code of conduct, contributing recipes, contributors file; name check done; advisor invitations drafted |

Numbers at close: 251 tests (250 passed, 1 skipped on macOS), coverage 92 percent including the sandboxed children; 18 techniques, 36 fixtures; every commit conventional, every story on its own branch merged with `--no-ff`; CI green on `dev`.

### Slipped

- US-019 (fixtures from PhantomText and CrackedPDFs): the generated fixtures covered every technique, and the external corpora belong with the benchmark; moved to week 5 with the corpus index (US-050). Board note added.
- US-022 (advisor invitations): drafts written; sending them is the owner's action.
- US-039 (v0.1.0 release): code complete; the release pull request, PyPI trusted publishing and the tag need the owner.

### Retro

- What slowed us: the first Notion seed used the brief's four use cases and had to be renumbered; a recreated select cleared 32 version fields.
- What went well: the THREATS.md contract test and the fixture pair rule caught two wrong fixtures (a grey-on-grey negative, a missing ToUnicode reference) before they became false claims.
- What to change: pull the View B work earlier in a week (stage 1 confirmation is what makes the detectors honest), which happened here by accident and should be the plan.
- Risk into week 2: v0.2.0 is the HTML report and its design; that work waits for the owner and a design pass.

## Planning (21 to 22 Sep 2026)

- Brief exported to `docs/00-brief/PROJECT_BRIEF.md` and corrected to v0.2 after a verified landscape pass.
- `CLAUDE.md` rewritten from the PermitFlow workflow and the brief: Notion board, `main` sacred, story branches from `dev`, one release per use case, the product contract.
- Notion board "Paperglass" with 7 epics and 90 stories (US-000 to US-099); `docs/05-planning/ISSUES.md` mirrors it.
- Railway project `paperglass` with `development` and `production` environments (nothing deployed until v0.4.0).
- Decisions recorded in `SCOPE.md`: five use cases, cascade View B, possible and confirmed findings, no score, subtractive `clean()`, fingerprint, profiles, MCP receipt gate, docs scan, false-positive bounty, glyph arbiter, disclosure ids; deferred items named.
- Docs tree scaffolded (`docs/README.md` lists status per document).

Handover (22 Sep 2026, end of session): everything through US-038 is merged on `dev` and pushed. Next: the owner configures PyPI trusted publishing for `paperglass` (pending publisher: repository SuhaasNv/paperglass, workflow release.yml, environment pypi), reviews the `dev` to `main` pull request, tags v0.1.0; then v0.2.0 starts with the HTML report design (US-037, US-043, US-044), which the owner wants to design with Fable before code.
