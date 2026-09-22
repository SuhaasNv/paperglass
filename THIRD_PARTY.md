# Third-party dependencies and licences

Every runtime dependency, its licence and why it is used. Permissive only: MIT, BSD, Apache-2.0, MPL-2.0. AGPL is banned (PyMuPDF). No gated model is a hard dependency. The table is updated in the same change that adds or removes a dependency; `pip-audit` runs in CI.

## Runtime (resolved by `uv lock` at US-000, 22 Sep 2026; adapter extras are pinned at their own stories)

| Package | Version | Licence | Used for | Extra |
|---------|---------|---------|----------|-------|
| pypdfium2 | 5.13.0 | Apache-2.0 or BSD-3 | PDF rendering and default View A extraction | core |
| pikepdf | 10.13.0.post1 | MPL-2.0 | View C: content streams, fonts, OCGs, annotations, metadata | core |
| fontTools | 4.65.0 | MIT | glyph names, cmap tables, glyph rendering for the arbiter | core |
| pdfplumber | 0.11.10 | MIT | alternate View A extractor | core |
| pypdf | 6.19.0 | BSD-3 | alternate View A extractor | core |
| pdfminer.six | 20260107 | MIT | alternate View A extractor (fingerprint) | core |
| python-docx | 1.2.0 | MIT | DOCX View A | core |
| lxml | 6.1.3 | BSD-3 | raw OOXML parts | core |
| puremagic | 2.2.0 | MIT | magic-byte sniffing | core |
| Pillow | 12.3.0 | HPND (MIT-like) | rasters, crops | core |
| numpy | 2.5.3 | BSD-3 | ink and contrast checks | core |
| rapidfuzz | 3.14.6 | MIT | alignment | core |
| pydantic | 2.13.5 | MIT | schemas | core |
| typer | 0.26.8 | MIT | CLI | core |
| jinja2 | 3.1.6 | BSD-3 | HTML report | core |
| rapidocr-onnxruntime | 1.4.4 | Apache-2.0 | OCR on crops | ocr |
| onnxruntime | 1.30.0 | MIT | OCR runtime | ocr |
| python-pptx | 1.0.2 | MIT | PPTX (v0.5.0) | pptx |
| selectolax | 0.4.12 | MIT | HTML DOM (v0.4.0) | html |
| fastapi, uvicorn | 0.141.1, 0.53.0 | MIT, BSD-3 | REST (v0.4.0) | rest |
| mcp | 2.2.0 | MIT | MCP server (v0.4.0) | mcp |
| datasets | 5.0.1 | Apache-2.0 | corpus index (v0.3.0) | bench |
| scikit-learn | 1.9.1 | BSD-3 | metrics (v0.3.0) | bench |
| reportlab | 5.0.1 | BSD-3 | Red Kit PDF generation (v0.5.0) | redkit |
| langchain-core, llama-index-core, docling | 0.3.86, 0.12.52, 2.129.0 | MIT, MIT, MIT | adapters (v0.4.0), pinned | langchain, llamaindex, docling |

Optional, user-installed, never imported by core: Prompt Guard 2 (Llama 4 Community Licence, gated); Florence-2 (MIT) or SmolVLM2 (Apache-2.0) for the deep tier.

## Corpora

| Source | Licence | Note |
|--------|---------|------|
| CrackedPDFs | MIT | v1 placement-label erratum noted in `docs/08-benchmark/CORPUS_INDEX.md` |
| PhantomText generated samples | MIT (toolkit) | attribution required |
| PhantomLint fixtures | BSD-3 | |
| Semantic Integrity canaries | by request from the authors | |
| Benign corpus sources | arXiv CC BY subset, SEC EDGAR (public domain), government circulars, accessibility samples | downloaded by script, not redistributed where a licence forbids |
