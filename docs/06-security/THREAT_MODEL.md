# Threat model: Paperglass as an attack surface

Every input is untrusted. Paperglass parses files written by adversaries and is deployed in front of the systems those adversaries target. Threats are to the scanner, to the people whose documents it reads, and to the honesty of its claims. Status per row: planned, built (date), validated (test).

| Id | Threat | Control | Validation | Status |
|----|--------|---------|------------|--------|
| T1 | A crafted file hangs a parser (infinite loop, pathological regex, deep nesting) | Subprocess with wall-clock and CPU limits; recursion depth caps; timeout is a `parse.failure` finding | `tests/unit/test_sandbox.py`; fuzz corpus | planned (US-003) |
| T2 | A crafted file exhausts memory (zip bomb, huge raster, object stream bomb) | Memory rlimit; file size and page caps; zip ratio check before extraction; render size capped by dpi and page size | fuzz corpus; a zip-bomb fixture | planned (US-003) |
| T3 | A memory-safety bug in a native parser (pdfium, qpdf, onnxruntime, Pillow) executes code | Subprocess isolation; pinned versions; `pip-audit` blocking; hardened REST image (network none, read-only, non-root); dependency policy of 30 days for critical CVEs | CI; image test | planned (US-003, US-066) |
| T4 | Document content is executed (PDF JavaScript, open actions, macros, external references, font programs) | Never evaluated; `pdf.active.content` flags and stops the carrier; no XObject or reference followed outside the file; fonts rasterised only by pdfium's sandboxed engine | code review; fixtures with JS and OpenAction | planned (US-017) |
| T5 | The scanner makes a network call (remote XObject, OCR model download, telemetry) | No network in parsers; `allow_network` reaches adapters only; no telemetry; tests run with sockets disabled | `tests/unit/test_no_network.py` | planned (US-003) |
| T6 | Document content leaks through logs, caches or reports | No content in logs by default; request ids; `--redact`; cache keyed by hash and holding rasters only; retention guidance | `tests/unit/test_logging.py` | planned (US-025) |
| T7 | Personal data of applicants and authors spreads (crops, extracted text in reports) | `--redact`; no real documents in fixtures; report copy describes the document, not the person; retention section in OPERATIONS.md | fixture audit | planned (US-025) |
| T8 | An attacker reads the public benign-hidden allowlist and hides the payload in an allowed channel | Allowlist is a class with constraints (length, phrasing, OCR agreement), never an exemption; constraint violations reclassify to the hiding technique; constraints are fixtures | benign fixtures plus violating fixtures | planned (US-020) |
| T9 | An attacker evades View B (makes text visible to the raster but not to a person: 1 pt, extreme margins, covered by a pattern) | Stage 1 thresholds tuned on the benign corpus; 200 dpi when small fonts present; covered-by-shape check; Red Kit grows the corpus | benchmark per technique; Red Kit | planned (US-030, US-075) |
| T10 | A structure-only heuristic (font decoding, reading order) produces false positives that block honest documents | Pinned to info; never drives a verdict alone; deep tier confirms | benign corpus false-positive split | planned (US-031) |
| T11 | The benchmark is gamed or leaks (detector trained on the test split; shortcut features) | Hard-provenance split by base document; unseen-generator split; label-shuffle check; shortcut audit; immutable versions with DOI | `docs/08-benchmark/BENCHMARK_DESIGN.md` | planned (US-053) |
| T12 | Numbers are published that do not reproduce or that hide a flag | One command from a clean clone; non-default flags stated; synthetic labelled; PhantomLint's phrase gate stated | release checklist | planned (US-055) |
| T13 | A malicious pull request adds a fixture that exploits the CI runner | Fixtures parsed only inside the sandbox in CI; CI permissions `contents: read`; no secrets in CI for pull requests | CI configuration | planned (US-004) |
| T14 | A repository document read by a coding agent carries invisible Unicode or hidden HTML (the docs-scan case) | `paperglass scan ./docs` in pre-commit and CI on this repository | US-079 | planned |
| T15 | Supply chain: a compromised dependency release | Pinned versions with hashes (`uv.lock`); `pip-audit`; gitleaks; trusted publishing to PyPI with no long-lived token | CI | planned (US-004, US-039) |
| T16 | The MCP or REST service is used to scan documents the caller should not have (a proxy for exfiltration) | The service returns findings, never the full document; request size caps; no persistence by default; receipts keyed by hash | `tests/adapters/test_rest.py` | planned (US-065, US-066) |

## Out of scope

Malware detection (ClamAV, YARA); the security of the pipeline that calls Paperglass; model-side defences (spotlighting) beyond consuming the provenance tags.

## Review

`SECURITY_REVIEW.md` (US-080, week 11) walks the rows with the test that proves each and runs four abuse scenarios: a zip bomb, a 10,000-page PDF, a font with an enormous glyph count, a file that is valid PDF and valid DOCX at once. Short, like everything else here.
