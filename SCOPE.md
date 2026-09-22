# SCOPE.md: Paperglass

**Decision in one line:** build a document trust scanner whose verdict is a proven discrepancy between what a parser extracts and what a person sees, ship it as five use-case releases over 12 weeks, and publish a benchmark other detectors can run. Cutting is allowed; silence is not. This file is the record and changes the moment scope changes.

Brief: `docs/00-brief/PROJECT_BRIEF.md` (version 0.2, 22 Sep 2026). Board: Notion "Paperglass", mirrored in `docs/05-planning/ISSUES.md`. Roadmap and cut order: `docs/05-planning/ROADMAP.md`.

## Why this scope

Three 2026 studies agree: hidden-document injection is in production (1 to 10 percent of resumes), every extractor is fooled by some subset of 25 known gaps, and phrase classifiers miss most of it because more than 90 percent of real injections are hidden data, not instructions. Nothing maintained, packaged, benchmarked and permissively licensed sits on the defence side. The scanner and the benchmark are two halves of one claim: to get past View B an attacker has to make the text visible, which is the one thing the attack cannot afford.

## Use cases and releases

The brief (v0.1) had four use cases. On 22 Sep 2026 the owner chose five, so that the use-case number is the release number, and Red Kit got its own use case because it serves a different person (a security tester generating samples) and ships its own deliverable. The brief's roadmap version numbers are superseded by this table.

| Release | Use case | Week | What ships |
|---------|----------|------|------------|
| v0.1.0 | UC1 Scan and Verdict (plus E0 Foundation) | 4 | PDF and DOCX; views A, B (cascade), C; possible and confirmed findings with mechanism and reproduce; MUST techniques; JSON report; `paperglass scan`, `fingerprint`, `show`; `--redact`; Python API; quiet PyPI release |
| v0.2.0 | UC2 Human-Readable Report | 5 | One-file offline HTML report with the word-aligned diff as centrepiece; profiles; the 30-second demo; Show HN |
| v0.3.0 | UC3 Benchmark and Leaderboard | 6 | Corpus index, benign corpus of at least 5,000 documents, hard-provenance and unseen-generator splits, shortcut audit, `paperglass bench`, baselines, `BENCHMARK.md`, dataset card and DOI, `results/` accepting pull requests, false-positive fixtures with credit |
| v0.4.0 | UC4 Pipeline Guard and Sanitise | 8 | LangChain, LlamaIndex, Docling adapters; HTML and Markdown; repository docs scan with pre-commit hook and GitHub Action; subtractive `clean()` with fidelity and Policy; MCP receipt gate; hardened Docker REST on Railway with Prometheus and Grafana; ATR ids and scan-target proposal; SARIF if cheap |
| v0.5.0 | UC5 Red Kit and Breadth | 10 | Red Kit for PDF and DOCX; PPTX; images and scans; glyph-level arbiter; stable technique ids with disclosure; benchmark v2 |
| v1.0.0 | E6 Community and Release | 12 | Security review and fuzzing pass, benchmark v1 frozen, docs site, ten good-first-issues, announcements |

## Stack and architecture (short)

One Python 3.11+ package, `paperglass`, with a sandboxed ingest, three view builders (A extract, B raster and OCR cascade, C structure), a discrepancy engine that promotes View C candidates from possible to confirmed, a report builder (JSON, HTML, SARIF) and adapters (CLI, Python API, LangChain, LlamaIndex, Docling, MCP, REST, GitHub Action). Layering `adapters -> engine -> views / detectors -> parsers` is enforced by a test. Dependencies are MIT, BSD, Apache-2.0 or MPL-2.0 only; PyMuPDF (AGPL) is banned; pypdfium2 renders and extracts. Full architecture: `docs/03-architecture/ARCHITECTURE.md`; the views: `docs/03-architecture/VIEWS.md`.

## MUST (v0.1.0 to v1.0.0)

| # | Feature | Release | Brief ref |
|---|---------|---------|-----------|
| M1 | PDF and DOCX inputs; type from magic bytes; configurable size and page caps; every parser call sandboxed; no execution of document content; no network by default | v0.1.0 | UC1 input and safety |
| M2 | View A pluggable (pypdfium2 default; pdfplumber, pypdf, pdfminer.six, Docling when installed); the report names the extractor | v0.1.0 | section 4 item 1, section 13 |
| M3 | View B cascade: raster ink check on every extracted run (no OCR), OCR on crops only, full-page OCR only in the deep tier; 150 dpi, 200 dpi when any font is under 6 pt; dpi in the report | v0.1.0 | section 9 (as amended 22 Sep) |
| M4 | View C probes for the MUST techniques in `THREATS.md`, each emitting a candidate with a named mechanism and a reproduce command | v0.1.0 | section 8 |
| M5 | Findings carry status possible or confirmed; verdict from confirmed findings only; verdicts clean, benign-hidden, suspicious, malicious; severity counts; no 0 to 100 score | v0.1.0 | UC1 detection (as amended) |
| M6 | Severity classes: instruction to a model (high or critical); hidden data injection (medium; high when it contradicts visible text); benign-hidden (info, constrained); structure-only (info, never alone) | v0.1.0 | section 9 (as amended) |
| M7 | JSON report validated against schema v1 with tool version, rule versions, extractor, page count, pages render-verified, dpi, SHA-256 | v0.1.0 | UC1 output |
| M8 | CLI `scan`, `fingerprint`, `show --object`, exit codes 0, 1, 2, 3; `--redact`; `--tier`; no telemetry | v0.1.0 | UC1 output |
| M9 | Fast tier at or below 100 ms per page (stages 0 and 1); standard tier p50 at or below 300 ms, p95 at or below 1 s on a 4-core CPU (plus stages 2 and 3) | v0.1.0 measured, v1.0.0 gated | section 11 |
| M10 | One positive and one negative fixture per technique; detector coverage at or above 90 percent; golden files; fuzz corpus green; layering test | v0.1.0 | section 11 |
| M11 | HTML report: one file, offline, no external requests, word-aligned diff of what the model reads and what a person sees, thumbnails with overlays, hidden text beside each, plain-language sentence per technique, mechanism per finding, label plus shape per severity, PDF export via the browser | v0.2.0 | UC2 (brief UC4) |
| M12 | Profiles resume, peer-review, rag-ingest | v0.2.0 | added 22 Sep |
| M13 | Unified corpus index (CrackedPDFs, PhantomText, Semantic Integrity canaries, PhantomLint fixtures, Red Kit) with labels, format, source, licence and hash; benign corpus at least 5,000 real documents with accessibility samples | v0.3.0 | UC3 corpus |
| M14 | Hard-provenance split by base document, unseen-generator split, shortcut audit, per-family reporting, data-injection recall separate from instruction recall | v0.3.0 | UC3 (as amended) |
| M15 | `paperglass bench` with the two-function adapter (scan, version); precision, recall, F1, per-technique recall, false-positive rate split into verdict-driving and informational, latency, fidelity column | v0.3.0 | UC3 harness |
| M16 | Baselines with exact commands: PhantomLint (with and without its phrase gate where possible), OpenDataLoader; DocFirewall if it installs cleanly; Prompt Guard 2 once as the phrase-only control | v0.3.0 | UC3 |
| M17 | `BENCHMARK.md` reproducible from a clean clone; dataset card (CC BY 4.0); Zenodo DOI; `results/` accepting pull requests; false-positive fixture bounty with credit | v0.3.0 | UC3 |
| M18 | LangChain document transformer, LlamaIndex node postprocessor and reader, Docling step, all with the metadata contract and tests against pinned versions | v0.4.0 | UC4 (brief UC2) |
| M19 | HTML and Markdown inputs; `paperglass scan ./docs` for repository documents; pre-commit hook; GitHub Action that fails on malicious | v0.4.0 | UC4, added 22 Sep |
| M20 | Subtractive `clean()` with provenance tags and a fidelity number (at least 99.9 percent benign words retained on the benign corpus); Policy pass, clean, block | v0.4.0 | UC4 sanitise (as amended) |
| M21 | MCP server with a scan receipt and a read gate; hardened Docker REST (network none, read-only, non-root) on Railway development and production | v0.4.0 | UC4 |
| M21a | Observability: Prometheus metrics from the REST service, Grafana dashboard and alert rules generated from scripts, Prometheus and Grafana as Railway services | v0.4.0 | added 22 Sep |
| M22 | ATR rule ids on findings where a rule fits; proposal for an ATR document-structure scan target | v0.4.0 | section 4 item 7 (as amended) |
| M23 | Red Kit generator for PDF and DOCX, seeded and deterministic, matched controls, one file plus a fixture pair adds a technique; benchmark v2 | v0.5.0 | UC5 (brief UC3 Red Kit) |
| M24 | PPTX views and techniques; glyph-level arbiter for ToUnicode and ActualText; stable pg.* technique ids with disclosure and a 30-day embargo | v0.5.0 | section 8, added 22 Sep |
| M25 | Security review and fuzzing pass recorded; benchmark v1 frozen and every baseline re-run; docs site; ten good-first-issues; recipes verified by a newcomer; announcements | v1.0.0 | section 11, 14 |
| M26 | Root documents: README with 60-second demo, SCOPE, THREATS, BENCHMARK, AI_USAGE, CHANGELOG, SECURITY (90-day policy), THIRD_PARTY, CONTRIBUTING with both recipes, CODE_OF_CONDUCT; every one describes what exists | every release | section 15 |

## SHOULD

| # | Feature | Release | Simplification if short |
|---|---------|---------|-------------------------|
| S1 | SARIF output | v0.4.0 | Only if the docs-scan Action makes it a two-hour job; otherwise after v1.0.0 |
| S2 | Images and scanned PDFs through OCR with a contrast sweep tuned on the benign corpus | v0.5.0 | Scans routed to the deep tier only |
| S3 | HTML web-font remapping detection (the HTML twin of the CMap remap) | v0.5.0 | Document as known gap |
| S4 | Reading-order splits (pdf.order.split), info severity | v0.5.0 | Document as known gap |
| S5 | Optional headless render for HTML View B | v0.5.0 | View C only for HTML |

## COULD (only if the core is stable)

| # | Feature |
|---|---------|
| C1 | Leaderboard Space on Hugging Face with a reviewed submission workflow (after v1.0.0; `results/` pull requests cover v0.3.0 to v1.0.0) |
| C2 | Deep tier with Florence-2 (MIT) or SmolVLM2 (Apache-2.0) for scans, opt-in, never default |
| C3 | Drag-and-drop web demo on the Railway REST service |
| C4 | SIEM export (JSON lines) and signed reports (sigstore) |
| C5 | Steganographic acrostics and microglyph patterns (statistical, research-grade) |
| C6 | Signed provenance record per scan |

## DEFERRED, with reasons

| Item | Reason | Owner of the problem |
|------|--------|----------------------|
| Semantic injections in fully visible text | A different problem; the hook exists so a classifier can raise severity | Prompt Guard, LLM Guard, ATR phrase rules |
| Malware, macros, active content | Presence is flagged in View C and the scan stops for that carrier | ClamAV, YARA, DocFirewall |
| Image steganography, adversarial pixels | No reliable open detector | research |
| Float-array carriers (arXiv 2606.08403) and any payload with no hidden text and no visual discrepancy | Outside the thesis by construction; named so the limit is explicit | classifiers, model-side defences |
| XLSX | Hidden sheets are DocFirewall's territory; spreadsheets rarely reach a model raw | after v1.0.0 |
| EML | Email is a different pipeline | after v1.0.0 |
| Unstructured and Haystack components | Adapters against monthly-churning APIs are a permanent tax; a plain function plus a notebook covers both | after v1.0.0 |
| arXiv technical report | Written a month after v1.0.0 when external submissions exist | after v1.0.0 |
| Multilingual instruction-phrase packs | Phrase lists are DocFirewall's strategy; phrase matching only raises severity here | community, after v1.0.0 |
| Image Red Kit generators | PDF and DOCX first | after v1.0.0 |
| A 0 to 100 trust score | A number invites ranking people and contradicts "never decides for a person"; verdict plus severity counts say everything the findings say | removed 22 Sep 2026 |
| Browser extension | A third platform for one maintainer; the offline HTML report covers the need | not planned |
| Trust-score history for repeated submitters | Needs identity and storage; turns a scanner into surveillance of applicants | not planned |
| Audio and video | Out of scope | not planned |

## Assumptions

- Every input is untrusted; the scanner is itself an attack surface and is built like one (`docs/06-security/THREAT_MODEL.md`).
- Same input, same tool version, same output; rule versions and content hashes in every report; golden files prove it.
- Hidden is not always malicious; benign-hidden is a class with public, tested constraints, never an exemption.
- The victim pipeline's parser may not be ours; View A is pluggable and `paperglass fingerprint` shows which parsers are fooled.
- One maintainer at 15 to 20 hours a week; the weekly plan never exceeds that and the cut order in `ROADMAP.md` is applied before a week is extended.
- Cash budget S$0 to S$150 for the 12 weeks; any paid service is asked for first.

## Scope checks (one dated paragraph per weekly close)

**22 Sep 2026, planning.** Brief v0.1 reviewed against the landscape (verified) and three research groups' method sections. Five use cases adopted; View B made a cascade; findings gained possible and confirmed; score removed; subtractive `clean()` with fidelity; fingerprint, mechanism and reproduce, profiles, MCP receipt gate, repository docs scan, false-positive bounty, glyph arbiter, technique disclosure added; leaderboard Space, Unstructured, Haystack, arXiv report, deep tier, multilingual packs, XLSX, EML, image Red Kit deferred; images moved from MUST to SHOULD. Show HN moves from v0.1.0 (week 4) to v0.2.0 (week 5). No code yet.
