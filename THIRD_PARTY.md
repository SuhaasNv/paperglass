# Third-party dependencies and licences

Every runtime dependency, its licence and why it is used. Permissive only: MIT, BSD, Apache-2.0, MPL-2.0. AGPL is banned (PyMuPDF). No gated model is a hard dependency. The table is updated in the same change that adds or removes a dependency; `pip-audit` runs in CI.

## Planned (no code yet; confirmed at US-000 and each adapter story)

| Package | Licence | Used for | Extra |
|---------|---------|----------|-------|
| pypdfium2 | Apache-2.0 or BSD-3 | PDF rendering and default View A extraction | core |
| pikepdf | MPL-2.0 | View C: content streams, fonts, OCGs, annotations, metadata | core |
| fontTools | MIT | glyph names, cmap tables, glyph rendering for the arbiter | core |
| pdfplumber | MIT | alternate View A extractor | core |
| pypdf | BSD-3 | alternate View A extractor | core |
| pdfminer.six | MIT | alternate View A extractor (fingerprint) | core |
| python-docx | MIT | DOCX View A | core |
| lxml | BSD-3 | raw OOXML parts | core |
| puremagic | MIT | magic-byte sniffing | core |
| Pillow | HPND (MIT-like) | rasters, crops | core |
| numpy | BSD-3 | ink and contrast checks | core |
| rapidfuzz | MIT | alignment | core |
| pydantic | MIT | schemas | core |
| typer | MIT | CLI | core |
| jinja2 | BSD-3 | HTML report | core |
| rapidocr-onnxruntime | Apache-2.0 | OCR on crops | ocr |
| onnxruntime | MIT | OCR runtime | ocr |
| python-pptx | MIT | PPTX (v0.5.0) | pptx |
| selectolax | MIT | HTML DOM (v0.4.0) | html |
| fastapi, uvicorn | MIT, BSD-3 | REST (v0.4.0) | rest |
| mcp | MIT | MCP server (v0.4.0) | mcp |
| datasets | Apache-2.0 | corpus index (v0.3.0) | bench |
| scikit-learn | BSD-3 | metrics (v0.3.0) | bench |
| reportlab | BSD-3 | Red Kit PDF generation (v0.5.0) | redkit |
| langchain-core, llama-index-core, docling | MIT, MIT, MIT | adapters (v0.4.0), pinned | langchain, llamaindex, docling |

Optional, user-installed, never imported by core: Prompt Guard 2 (Llama 4 Community Licence, gated); Florence-2 (MIT) or SmolVLM2 (Apache-2.0) for the deep tier.

## Corpora

| Source | Licence | Note |
|--------|---------|------|
| CrackedPDFs | MIT | v1 placement-label erratum noted in `docs/08-benchmark/CORPUS_INDEX.md` |
| PhantomText generated samples | MIT (toolkit) | attribution required |
| PhantomLint fixtures | BSD-3 | |
| Semantic Integrity canaries | by request from the authors | |
| Benign corpus sources | arXiv CC BY subset, SEC EDGAR (public domain), government circulars, accessibility samples | downloaded by script, not redistributed where a licence forbids |
