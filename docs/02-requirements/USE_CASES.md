# Use cases

Five use cases; the use-case number is the release number (`SCOPE.md`). Each lists background, the story in one sentence, acceptance criteria, and the stories on the board that implement it (`../05-planning/ISSUES.md`). The brief (v0.1) numbered them differently; the mapping is in the brief's revision note.

## UC1 Scan and Verdict (v0.1.0, week 4)

**Background.** A developer receives files from strangers and feeds them to a model. They need to know, before the model reads, whether the file says something to the model that it does not say to a person, and they need to be able to prove it.

*As a developer, I want to scan a document and get a verdict with evidence I can reproduce, so that I can block, sanitise or accept it with a reason I can show to someone else.*

Acceptance criteria:
- Input: path, bytes or stream; type from magic bytes; configurable size and page caps; every parser call sandboxed; never executes document content; no network unless `allow_network`.
- Views A, B (cascade: ink check on every run, OCR on crops) and C run per page; View C candidates are `possible` until View B or a self-proving mechanism confirms them.
- Every finding carries technique id, status, page, bbox, extracted text, rendered crop (or none with a reason), why-hidden, mechanism (the exact object), reproduce (a command), severity, confidence, ATR id where one exists.
- Verdict is one of clean, benign-hidden, suspicious, malicious, from confirmed findings only, with severity counts; there is no numeric score.
- JSON report validated against schema v1 with tool version, rule versions, extractor, page count, pages render-verified, dpi, SHA-256.
- CLI `paperglass scan` with exit codes 0, 1, 2, 3; `paperglass fingerprint` prints which installed extractors return each hidden run; `paperglass show --object` prints the object behind a finding; `--redact`; `--tier fast|standard|deep`.
- Fast tier at or below 100 ms per page; standard p50 at or below 300 ms on a 4-core CPU (measured and published; gated at v1.0.0).
- PDF and DOCX; every MUST technique in `THREATS.md` for those formats has a fixture pair and a row.
- No telemetry; no document content in logs.

Stories: US-000 to US-025, US-030 to US-039 (E0 and UC1).

## UC2 Web app and report (v0.2.0, week 5)

**Background.** Recruiters, journal editors, loan officers and licensing officers are the people who sign. They need to see the trick, not a JSON file, and they must not be handed a number to rank people by. Developers evaluating the scanner want to drop a file in a browser before they install anything. Both need the same screen.

*As a reviewer or a curious developer, I want to upload a document in the browser and see the page, what was hidden, what it said and how it was hidden, so that I can decide with my own eyes and share the result with a link.*

Acceptance criteria:
- Backend: FastAPI + SQLAlchemy 2 + Alembic + PostgreSQL. `POST /api/v1/scans` (multipart upload, tier, profile) scans in memory through `paperglass.engine.scan_bytes` and stores the report under an unguessable id; `GET /api/v1/scans/{id}` returns the report; `GET /api/v1/scans/{id}/fingerprint` runs and caches the fingerprint; `GET /api/v1/scans/{id}/report.html` returns the one-file offline HTML report; `GET /api/v1/scans` lists the current browser's scans (anonymous session cookie); `GET /healthz`; `GET /metrics` behind a token (US-089). Files are never written to disk or the database; reports expire after 7 days; standard error body; request id on every log line; size cap; no accounts.
- Frontend: React 19 + TypeScript strict + Vite + Tailwind + TanStack Query. Screens: upload (drag and drop, tier and profile), results (verdict and severity counts on top; the word-aligned diff of what the model reads against what a person sees as the centrepiece, every unmatched run highlighted and clickable to its crop; finding cards with the plain sentence, mechanism, reproduce command and crop; a pages tab with overlays; a fingerprint tab), history (this browser's scans), techniques (every `THREATS.md` row in plain language), about. Every severity uses a label plus a shape; copy says "hidden text found", never "fraud" or "cheating"; benign-hidden is never labelled an attack; no em dashes, no emoji. Screens are built to the design the owner settles with Fable.
- Downloadable one-file HTML report: no external requests, opens offline, the same diff and cards, PDF export via the browser.
- Profiles resume, peer-review and rag-ingest set thresholds, phrase packs and expected benign-hidden content; selectable in the app and the CLI; the profile is named in the report.
- Delivery: Docker images for backend and frontend on GHCR; Railway `development` (auto from `dev`) and `production` (from `main`, approval gate) each with its own Postgres; health gate; CI adds frontend lint, typecheck, vitest, the Playwright journey at 375, 768 and 1280 px, and the image build.
- The 30-second demo is recorded in the web app from the demo documents in `../13-demo/` and Show HN goes out with this release.

Stories: US-037, US-040 (if cheap), US-041 to US-049.

## UC3 Benchmark and Leaderboard (v0.3.0, week 6)

**Background.** Every existing detector reports numbers on its own samples. Without a shared corpus and harness no claim can be compared, and attackers adapt faster than defenders publish.

*As a researcher or maintainer, I want to run any detector over one public corpus and publish comparable numbers, so that progress is measurable and the benchmark grows faster than the attacks.*

Acceptance criteria:
- Unified index over CrackedPDFs (with its erratum noted), PhantomText samples (MIT, attributed), Semantic Integrity canaries (by request, or rebuilt from the paper), PhantomLint fixtures and Red Kit samples; each sample has technique labels, format, source, licence and a hash.
- Benign corpus of at least 5,000 real documents with legitimate hidden content represented (tagged PDFs, scans with OCR layers, accessible DOCX).
- Hard-provenance split by base document; unseen-generator split; label-shuffle check; shortcut audit; per-family reporting; data-injection recall separate from instruction recall.
- `paperglass bench` runs any detector implementing the two-function adapter (scan, version) and prints precision, recall, F1, per-technique and per-family recall, false positives split into verdict-driving and informational, latency, and a fidelity column.
- Baselines with exact commands: PhantomLint (with and without its phrase gate where possible), OpenDataLoader; DocFirewall if it installs cleanly; Prompt Guard 2 once as the phrase-only control.
- `BENCHMARK.md` reproduces from a clean clone with one command; dataset card on Hugging Face (CC BY 4.0); Zenodo DOI; `results/` accepts pull requests with a results file and a reproducible command; a CI badge any detector can earn.
- A wrongly flagged real, redistributable document becomes a permanent negative fixture within a week, with credit.
- The four research groups receive their numbers before they are published.

Stories: US-050 to US-059.

## UC4 Pipeline Guard and Sanitise (v0.4.0, week 8)

**Background.** RAG loaders and agents ingest documents automatically. Blocking every suspicious file breaks the product; reading the invisible layer breaks security; replacing the text with OCR breaks fidelity. The pipeline needs a fourth option: keep the caller's text, remove only what was proven hidden, and tag the rest.

*As a RAG or agent builder, I want a drop-in step that removes what a person cannot see and tags what remains, so that my pipeline keeps working on the honest part of every document.*

Acceptance criteria:
- LangChain document transformer: documents pass through, metadata gains `paperglass.verdict`, `paperglass.severity_counts`, finding ids and provenance tags; text replaced by the clean view when policy says so. LlamaIndex node postprocessor and reader wrapper, and the Docling pipeline step, carry the same contract. Tests against pinned versions.
- HTML and Markdown inputs; `paperglass scan <dir>` checks repository documents (README, SKILL.md, CLAUDE.md, MCP tool descriptions) for invisible Unicode, hidden DOM and comments; pre-commit hook; GitHub Action that fails on malicious; this repository runs it on itself.
- `clean()` is subtractive: it takes the caller's extractor output, removes only confirmed-invisible runs, keeps structure, tags every run visible-confirmed, benign-hidden, structure-only or removed, and reports words kept, words removed and fidelity; at least 99.9 percent of benign words retained on the benign corpus. Policy pass, clean, block acts on verdict and severity counts; defaults documented.
- MCP server: `scan_document` returns a receipt (hash, verdict, rule versions, pages verified); `read_document` returns text only for a hash with a clean or benign-hidden receipt; passes the conformance suite.
- The REST service (built in UC2) gains API keys and rate limits for pipelines, a hardened image (the scanner worker with network none, read-only, non-root); no latency commitment until after v1.0.0.
- Observability: `/metrics` in Prometheus format behind a token; Prometheus and Grafana as Railway services and under a local compose profile; dashboard and alert rules generated from scripts.
- Findings carry ATR rule ids where a phrase-level rule fits; a document-structure scan target is proposed to the ATR registry with Paperglass as reference implementation.
- SARIF output if the docs-scan Action makes it a two-hour job.

Stories: US-040, US-060 to US-069, US-072, US-079, US-089.

## UC5 Red Kit and Breadth (v0.5.0, week 10)

**Background.** A public benchmark teaches attackers. The only answer is to grow the corpus faster than the attacks and to make the structural detection sharp enough that evasion means visibility. The remaining formats and the glyph arbiter belong here.

*As a security tester, I want a deterministic generator of new attack samples with matched controls, and detection that reaches the semantic-override family, so that my pipeline is tested against tomorrow's tricks and the benchmark keeps up.*

Acceptance criteria:
- Red Kit generates injected and matched-control samples from seeds for PDF and DOCX; the seed is in the file name; one file plus a fixture pair adds a technique; the benchmark version bumps to v2 with a new DOI.
- PPTX views and techniques (hidden slides, off-slide shapes, notes); images and scans through OCR with a contrast sweep tuned on the benign corpus.
- Glyph-level arbiter: each suspect glyph rendered from its embedded font and compared with the declared Unicode's canonical shape; ActualText spans OCRed alone; ToUnicode and ActualText findings promoted from possible to confirmed with a defensible false-positive rate, validated on the 25 canaries and the benign corpus; the HTML web-font twin as SHOULD.
- Stable technique ids with a plain-language page, a Red Kit reproduction, a first-seen date, cross-references to ATR, CrackedPDFs, PhantomText and Semantic Integrity ids, and a 30-day embargo for new techniques through `SECURITY.md`.

Stories: US-035, US-070, US-073, US-075, US-077, US-078, US-087, US-088.

## Launch (v1.0.0, week 12, epic E6)

Security review and fuzzing pass recorded; benchmark v1 frozen and every baseline re-run on the final detectors; docs site; ten good-first-issues; recipes verified by a newcomer; production readiness review, brief traceability and final review written honestly; announcements (OWASP GenAI, ATR, Hugging Face blog, talk proposal). Stories: US-080 to US-086.

## Constraints across all use cases

Paperglass is a detector and sanitiser; it never decides an outcome for a person. Offline by default; any network feature is opt-in and named in the report. Every claim in `BENCHMARK.md` is reproducible with one command from a clean clone. Repository copy passes `scripts/check_copy.py`.
