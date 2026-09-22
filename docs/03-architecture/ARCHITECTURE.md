# Architecture

One Python package, `paperglass`, with a pipeline of pure detectors behind one adapter surface. Status: skeleton built at US-000 (22 Sep 2026); the pipeline itself lands story by story and this file is amended as each piece exists.

## Pipeline

```
input (path | bytes | stream)
  -> ingest: magic-byte sniff, size and page caps, sandbox launch
  -> stage 0  parse:      View A runs (text, bbox, font, offset) + View C candidates (mechanism named)
  -> stage 1  ink check:  render once; classify every run visible | invisible | uncertain (no OCR)
  -> stage 2  OCR crops:  invisible and uncertain runs only; rapidfuzz alignment per font-size band
  -> stage 3  glyph:      suspect fonts rendered per glyph and compared with declared Unicode (cached)
  -> stage 4  deep:       full-page OCR, optional small vision model (opt-in)
  -> engine:  promote candidates possible -> confirmed; severity class; benign-hidden constraints; verdict
  -> report:  JSON (schema v1), HTML, SARIF; clean() with provenance
  -> adapters: CLI, Python API, LangChain, LlamaIndex, Docling, MCP, REST, GitHub Action
```

Tiers: fast = stages 0 and 1; standard = plus 2 and 3; deep = plus 4. Full detail in `VIEWS.md`.

## Packages (as built at US-000, 22 Sep 2026; modules fill in per story)

```
src/paperglass/
  ingest/        sniff, caps, sandbox context manager, parse.failure
  parsers/       thin wrappers around pypdfium2, pikepdf, fontTools, python-docx, lxml, selectolax
  views/
    extract/     View A backends (pypdfium2, pdfplumber, pypdf, pdfminer, docling, opendataloader)
    render/      raster, ink check, crops, OCR (RapidOCR), glyph arbiter
    structure/   View C probes per format
  detectors/     one module per technique id, @technique registration, Finding emission
  engine/        alignment, promotion, severity classes, allowlist constraints, verdict, clean()
  report/        schema models, JSON, HTML (jinja2), SARIF, explanations
  adapters/      cli, api, langchain, llamaindex, docling, mcp, rest, action
  bench/         corpus index, harness, metrics, baselines
  redkit/        generators
  profiles/      resume.toml, peer_review.toml, rag_ingest.toml, default.toml
```

## Layering rule (enforced by `tests/unit/test_layering.py`)

`adapters -> engine -> views / detectors -> parsers`. Detectors never import adapters. `engine` never imports `report`. `report` reads models only. Nothing imports a network client except `adapters`, and only behind `allow_network=True`. `profiles` and `report/explanations` are data, importable by anyone.

## Adapter table

| Adapter | Entry point | Contract | Release | Doc |
|---------|-------------|----------|---------|-----|
| CLI | `paperglass` (typer) | `scan`, `fingerprint`, `show`, `report`, `clean`, `bench`; exit codes 0 to 3 | v0.1.0 (scan, fingerprint, show), v0.2.0 (report), v0.3.0 (bench), v0.4.0 (clean) | `../04-report-design/CLI_DESIGN.md` |
| Python API | `paperglass.scan`, `.fingerprint`, `.clean`, `.report` | returns `Report` and `CleanResult` models | v0.1.0 | this file |
| LangChain | `PaperglassTransformer` | metadata keys `paperglass.verdict`, `paperglass.severity_counts`, `paperglass.findings`, provenance tags; text replaced per Policy | v0.4.0 | `../11-integrations/LANGCHAIN.md` |
| LlamaIndex | `PaperglassPostprocessor`, `PaperglassReader` | same keys | v0.4.0 | `../11-integrations/LLAMAINDEX.md` |
| Docling | pipeline step | same keys; Docling also usable as a View A extractor | v0.4.0 | `../11-integrations/DOCLING.md` |
| MCP | `paperglass-mcp` | `scan_document` (receipt), `read_document` (gated), `clean_document` | v0.4.0 | `../11-integrations/MCP.md` |
| REST | `paperglass-server` (fastapi) | `/v1/scan`, `/v1/clean`, `/healthz`; error body `{ "error": { "code", "message", "details"? } }` | v0.4.0 | `../11-integrations/REST.md` |
| GitHub Action | `action.yml` | scans a directory, fails on malicious, uploads SARIF if present | v0.4.0 | `../11-integrations/GITHUB_ACTION.md` |
| pre-commit | `.pre-commit-hooks.yaml` | fast tier over repository documents | v0.4.0 | `../11-integrations/GITHUB_ACTION.md` |

## Cross-cutting rules

Deterministic output; rule versions and the input hash in every report; no network by default; no document content in logs; every parser call inside the sandbox (`SANDBOX.md`); one detector per technique id (`TECHNIQUE_REGISTRY.md`); every schema change is a version bump with regenerated golden files (`FINDING_SCHEMA.md`).
