# Requirements

Each row: id, requirement, the release it ships in, how it is proven. "Proven by" names a test path or a command that will exist; until it exists the row is a promise.

## Functional (FR)

| Id | Requirement | Release | Proven by |
|----|-------------|---------|-----------|
| FR-001 | Accept a path, bytes or a stream; sniff the type from magic bytes, never the extension | v0.1.0 | `tests/unit/test_ingest.py` |
| FR-002 | View A returns positioned text runs (text, bbox, font ref, content-stream offset) from a pluggable extractor; the report names the extractor | v0.1.0 | `tests/unit/views/test_extract.py` |
| FR-003 | View B stage 1 classifies every extracted run visible, invisible or uncertain from the raster without OCR | v0.1.0 | `tests/unit/views/test_ink.py` |
| FR-004 | View B stage 2 runs OCR on crops of invisible and uncertain runs only; full-page OCR only in the deep tier | v0.1.0 | `tests/unit/views/test_ocr_crops.py` |
| FR-005 | View C probes emit candidates with a named mechanism for every MUST technique in `THREATS.md` | v0.1.0 | `tests/unit/detectors/test_<technique>.py` per row |
| FR-006 | Every finding carries status possible or confirmed; the verdict is derived from confirmed findings only | v0.1.0 | `tests/unit/engine/test_verdict.py` |
| FR-007 | Every finding carries technique id, page, bbox, extracted text, rendered crop or none with reason, why-hidden, mechanism, reproduce, severity, confidence, ATR id or none | v0.1.0 | schema test and golden files |
| FR-008 | Verdicts: clean, benign-hidden, suspicious, malicious; severity counts; no numeric score | v0.1.0 | `tests/unit/engine/test_verdict.py` |
| FR-009 | Severity classes: instruction (high or critical), data (medium, high on contradiction), benign-hidden (info), structure-only (info, never alone) | v0.1.0 | `tests/unit/engine/test_severity.py` |
| FR-010 | JSON report validated against schema v1 with tool version, rule versions, extractor, page count, pages render-verified, dpi, SHA-256 | v0.1.0 | golden files |
| FR-011 | CLI `scan`, `fingerprint`, `show --object`; exit codes 0, 1, 2, 3; `--tier`, `--redact` | v0.1.0 | `tests/adapters/test_cli.py` |
| FR-012 | `paperglass fingerprint` runs every installed extractor and prints which return each hidden run | v0.1.0 | `tests/adapters/test_fingerprint.py` |
| FR-013 | Python API `paperglass.scan()`, `paperglass.fingerprint()` | v0.1.0 | `tests/unit/test_api.py` |
| FR-014 | DOCX View A and C (vanish, colour, tiny, hidden parts) | v0.1.0 | fixtures under `tests/fixtures/docx/` |
| FR-015 | HTML report: one file, offline, no external requests, word-aligned diff, overlays, hidden text beside each region, plain sentence and mechanism per finding, verdict and counts on top, PDF export | v0.2.0 | `tests/report/test_html.py`, manual offline check at three widths |
| FR-016 | Profiles resume, peer-review, rag-ingest, selectable by `--profile` and named in the report | v0.2.0 | `tests/unit/test_profiles.py` |
| FR-017 | `paperglass bench` runs any detector implementing scan and version over a corpus version and prints the metrics in BENCH-004 | v0.3.0 | `tests/bench/test_harness.py` |
| FR-018 | LangChain document transformer, LlamaIndex node postprocessor and reader, Docling step, with the metadata contract | v0.4.0 | `tests/adapters/test_<adapter>.py` against pinned versions |
| FR-019 | HTML and Markdown inputs; `paperglass scan <dir>` over repository documents; pre-commit hook; GitHub Action failing on malicious | v0.4.0 | `tests/adapters/test_docs_scan.py`, the repository's own workflow |
| FR-020 | `clean()` subtractive with provenance tags per run and a fidelity number; Policy pass, clean, block | v0.4.0 | `tests/unit/engine/test_clean.py`, golden files |
| FR-021 | MCP server: `scan_document` returns a receipt; `read_document` returns text only for a hash with a clean or benign-hidden receipt | v0.4.0 | `tests/adapters/test_mcp.py`, conformance suite |
| FR-022 | REST: `/v1/scan`, `/v1/clean`, `/healthz`; error body `{ "error": { "code", "message", "details"? } }`; request id on every log line | v0.4.0 | `tests/adapters/test_rest.py` |
| FR-022a | `/metrics` in Prometheus format behind a token; Prometheus and Grafana as services; generated dashboard and alert rules | v0.4.0 | `tests/adapters/test_metrics.py`, `docs/15-observability/OBSERVABILITY.md` |
| FR-023 | Red Kit: seeded generator for PDF and DOCX with matched controls; one file plus a fixture pair adds a technique | v0.5.0 | `tests/redkit/test_determinism.py` |
| FR-024 | PPTX views and techniques; images and scans through the contrast sweep | v0.5.0 | fixtures |
| FR-025 | Glyph-level arbiter promotes ToUnicode and ActualText candidates to confirmed | v0.5.0 | canaries, benign corpus |
| FR-026 | Stable technique ids with plain-language page, reproduction, first-seen date, cross-references, 30-day embargo | v0.5.0 | `THREATS.md` and `docs/03-architecture/TECHNIQUE_REGISTRY.md` |

## Non-functional (NFR)

| Id | Requirement | Release | Proven by |
|----|-------------|---------|-----------|
| NFR-001 | Deterministic: same input, same tool version, same output | v0.1.0 | golden files |
| NFR-002 | Fast tier at or below 100 ms per page; standard p50 at or below 300 ms and p95 at or below 1 s on a 4-core CPU | measured v0.1.0, gated v1.0.0 | `bench/perf/` with the hardware named |
| NFR-003 | `pip install paperglass` has no binary dependency; `paperglass[ocr]` adds View B | v0.1.0 | CI install job on three operating systems |
| NFR-004 | Python 3.11+, mypy strict, ruff clean, no `Any` in public signatures, no bare except | v0.1.0 | CI |
| NFR-005 | Detector coverage at or above 90 percent; layering test green | v0.1.0 | CI `--cov-fail-under` |
| NFR-006 | Works on Linux, macOS and Windows (OCR jobs Linux and macOS until v1.0.0) | v0.1.0 | CI matrix |
| NFR-007 | Offline by default; network only behind `allow_network` and named in the report | v0.1.0 | `tests/unit/test_no_network.py` |
| NFR-008 | No telemetry, ever | v0.1.0 | code review, `SECURITY.md` |
| NFR-009 | Adapters are optional extras with their own pinned CI; a broken adapter is marked unsupported rather than blocking a release | v0.4.0 | `docs/10-operations/OPERATIONS.md` |

## Security (SEC)

| Id | Requirement | Release | Proven by |
|----|-------------|---------|-----------|
| SEC-001 | Every parser call runs in a subprocess with CPU, memory and wall-clock limits (5 s, 512 MB default), page and size caps, zip-bomb and recursion guards; a crash is a `parse.failure` finding | v0.1.0 | `tests/unit/test_sandbox.py`, fuzz corpus |
| SEC-002 | No execution of document content: no PDF JavaScript, no macros, no external references, no font programs outside the renderer | v0.1.0 | code review, `pdf.active.content` stops the carrier |
| SEC-003 | Fuzz corpus of malformed PDF, DOCX (and later PPTX, HTML) runs in CI without crash or hang | v0.1.0 | `tests/fuzz/` |
| SEC-004 | No document content in logs by default; `--redact` blanks crops outside findings | v0.1.0 | `tests/unit/test_logging.py` |
| SEC-005 | No secrets in the repository; gitleaks over full history and pip-audit block CI | v0.1.0 | CI |
| SEC-006 | Hardened REST image: `--network none` recommended, read-only filesystem, non-root, size caps | v0.4.0 | `docs/11-integrations/REST.md`, image test |
| SEC-007 | Private disclosure channel, 90-day policy, 30-day embargo for new techniques | v0.1.0 doc, v0.5.0 process | `SECURITY.md` |
| SEC-008 | Dependency policy: permissive licences only; a library with an unpatched critical CVE is dropped or pinned within 30 days | ongoing | `THIRD_PARTY.md`, pip-audit |

## Benchmark (BENCH)

| Id | Requirement | Release | Proven by |
|----|-------------|---------|-----------|
| BENCH-001 | Corpus index with technique labels, format, source, licence and hash per sample | v0.3.0 | `docs/08-benchmark/CORPUS_INDEX.md`, dataset card |
| BENCH-002 | Benign corpus of at least 5,000 real documents with accessibility samples | v0.3.0 | download script, count in `BENCHMARK.md` |
| BENCH-003 | Hard-provenance split by base document, unseen-generator split, label-shuffle check, shortcut audit, per-family reporting | v0.3.0 | `docs/08-benchmark/BENCHMARK_DESIGN.md`, harness output |
| BENCH-004 | Metrics: precision, recall, F1, per-technique and per-family recall, data-injection versus instruction recall, false positives split verdict-driving versus informational, latency, fidelity | v0.3.0 | harness output |
| BENCH-005 | Baselines with exact commands and non-default flags stated | v0.3.0 | `docs/08-benchmark/BASELINES.md` |
| BENCH-006 | Every number in `BENCHMARK.md` reproduces from a clean clone with one command; synthetic labelled synthetic; versions immutable with a DOI | v0.3.0 | release checklist |
| BENCH-007 | `results/` accepts pull requests carrying a results file plus a reproducible command | v0.3.0 | CI check |
| BENCH-008 | A wrongly flagged real document becomes a negative fixture within a week with credit; CI fails on regression | v0.3.0 | `tests/fixtures/false-positives/` |

## Report (REP)

| Id | Requirement | Release | Proven by |
|----|-------------|---------|-----------|
| REP-001 | Plain-language sentence per technique from one source shared by `THREATS.md` and the report | v0.2.0 | registry test |
| REP-002 | Every severity uses a label plus a shape; colour never carries meaning alone | v0.2.0 | `docs/04-report-design/ACCESSIBILITY.md`, manual check |
| REP-003 | No em dashes, no emoji, no decorative icons in report or docs copy | every release | release checklist grep |
| REP-004 | Report copy says "hidden text found", never "fraud" or "cheating"; benign-hidden is never labelled an attack | v0.2.0 | copy test |
| REP-005 | Report opens from `file://` with the browser offline at 375, 768 and 1280 px without horizontal scroll; prints to PDF | v0.2.0 | manual check recorded in the story |
| REP-006 | SARIF 2.1.0 output with one rule per technique id | v0.4.0 if cheap | golden file |
