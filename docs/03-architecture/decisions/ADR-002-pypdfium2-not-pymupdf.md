# ADR-002: pypdfium2 for rendering and default extraction; pikepdf and fontTools for structure

Date 22 Sep 2026. Status: accepted, not yet built (US-006, US-007, US-030).

## Context
View B needs a renderer whose output matches what people see; View A needs a default extractor that behaves like common pipelines; View C needs object-level access to content streams, fonts and CMaps. ADR-001 bans AGPL.

## Constraints
Permissive licence; wheels on Linux, macOS and Windows; deterministic rasters; no JavaScript execution.

## Options considered
### Option A: pypdfium2 (render and extract) plus pikepdf (objects) plus fontTools (glyphs)
- Pros: pdfium is the renderer in Chrome and most viewers, so View B is what a person sees; Apache-2.0/BSD; prebuilt wheels; pikepdf (MPL-2.0) exposes every object and content stream; fontTools (MIT) reads cmap tables and can rasterise glyphs for the arbiter.
- Cons: three libraries instead of one; pdfium text extraction is one of the parsers most fooled (22 of 25 gaps), which is exactly why it is a good default View A.
### Option B: PyMuPDF
- Pros: one library, fast, rich API.
- Cons: AGPL-3.0; PhantomLint's authors name it as an adoption limit.
### Option C: Poppler via pdftoppm plus pdfminer
- Pros: mature.
- Cons: system dependency (Tesseract and Poppler limited PhantomLint's adoption); no glyph access.

## Decision
Option A. pypdfium2 renders every page once and is the default View A; pdfplumber, pypdf and pdfminer.six are alternate View A backends; pikepdf walks content streams for View C; fontTools reads and rasterises glyphs for stage 3.

## Rationale
View B must match a viewer, View A must match a common pipeline, and both must install with `pip` and nothing else.

## Consequences
### Positive
`pip install paperglass` works with no system packages; fast tier has under ten dependencies.
### Negative
Rasterising a glyph outside pdfium for the arbiter needs fontTools' rasteriser or a pdfium single-glyph render; decided at US-087.

## Validation
Install job on three operating systems in CI; golden rasters per fixture.
