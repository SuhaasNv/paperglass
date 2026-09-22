# THREATS.md: Threat coverage matrix

One row per technique. A technique is covered only when the code has a detector registered with `@technique(...)` under that id, a positive and a negative fixture under `tests/fixtures/<format>/<technique>/`, and this row; a test fails when the three disagree. Status values: **planned** (story on the board, no detector), **partial** (detector exists with a fixture pair; the gap is named in the row), **covered** (every view the row names, fixtures green, benchmark numbers in `BENCHMARK.md`). The registry test compares the second and fourth columns of every row with the detector's registration character for character. The plain-language sentence is the one shown in the report; it is the single source (`docs/03-architecture/TECHNIQUE_REGISTRY.md`).

Views: A is what extractors return; B is the rendered page, checked for ink and then read by OCR on crops; C is document structure. Stage numbers refer to the cascade in `docs/03-architecture/VIEWS.md`. Severity class: **instruction** (an instruction addressed to a model; high or critical), **data** (hidden data injection; medium, high when it contradicts visible text), **structure-only** (info; never drives a verdict alone), **benign-hidden** (info; constrained allowlist). ATR: the Agent Threat Rules id where a phrase-level rule fits; `none` where the registry has no scan target for document structure (proposal pending, US-068).

Thresholds are the defaults; profiles (`docs/04-report-design/REPORT_DESIGN.md`) may tighten them.

## PDF

| Technique id | Plain language | View, stage | Threshold or mechanism | Class | ATR | Release | Status |
|--------------|----------------|-------------|------------------------|-------|-----|---------|--------|
| `pdf.text.low_contrast` | Text painted in a colour a person cannot tell from the background | B stage 1, C | fill within 24/255 of the local background; fill colour from the text state | data or instruction | ATR-2026-00515 (phrase part only) | v0.1.0 | partial (View C; View B confirmation at US-030) |
| `pdf.text.tiny` | Text too small for a person to read | B stage 1, C | effective font size after the CTM below 2 pt, or zero | data or instruction | none | v0.1.0 | partial (View C; View B at US-030) |
| `pdf.text.offpage` | Text placed outside the visible page or cut off by a clip | B stage 1, C | bbox outside MediaBox or CropBox, or fully clipped | data or instruction | none | v0.1.0 | partial (View C; View B at US-030) |
| `pdf.render.mode` | Text drawn in a mode that paints nothing (mode 3) or only sets a clip (mode 7) | C (self-proving), B stage 1 | `Tr 3` or `Tr 7` with extractable text; OCR text layers on scans are benign-hidden when they match the render | data or instruction | none | v0.1.0 | partial (self-proving; OCR-layer allowlist at US-020) |
| `pdf.text.opacity` | Text made almost transparent | B stage 1, C | ExtGState `ca` or `CA` below 0.1, or a blend mode that hides the text | data or instruction | none | v0.1.0 | partial (alpha only; blend modes to be written) |
| `pdf.layer.hidden` | Text on a layer that is switched off | C (self-proving) | optional content group in the default OFF array, or `/OC` marked content whose OCG is OFF | data or instruction | none | v0.1.0 | covered |
| `pdf.text.covered` | Text hidden under a shape or image drawn on top of it | B stage 1 and 2 | run extracted but no ink at its bbox after a later fill or image | data or instruction | none | v0.1.0 | partial (stage 1 raster rule; images drawn over text confirmed at stage 2 to be written) |
| `pdf.font.tounicode_mismatch` | The font tells the model different letters than it draws | C, then stage 3 | ToUnicode CMap maps a glyph to a code point whose canonical shape differs from the painted glyph; possible at stage 0, confirmed by the glyph arbiter | structure-only until confirmed; then data or instruction | none | v0.1.0 possible, v0.5.0 confirmed | partial (static encoding check, possible only; the glyph arbiter at US-087 confirms) |
| `pdf.actualtext.override` | A hidden replacement text overrides what the page shows | C, then stage 2 on the span | `/ActualText` differs from the painted glyphs; ligatures and hyphenation are benign-hidden when the ActualText is at most a few characters | structure-only until confirmed | none | v0.1.0 possible, v0.5.0 confirmed | partial (possible at stage 0; stage 2 OCR of the span confirms in the standard tier) |
| `pdf.font.decoding_fallback` | A font the extractor cannot decode, so the model may read garbage or the wrong words | C, deep tier B | Type 3, composite or CID font without a usable ToUnicode; extractors disagree (`paperglass fingerprint`) | structure-only (info; TeX Type 3 fonts are the known benign case) | none | v0.1.0 | partial (font table rule; per-extractor disagreement at US-023) |
| `pdf.order.split` | The order the text is stored in differs from the order a person reads it | A versus B ordering, deep tier | content stream order differs from layout order beyond a threshold | structure-only (info) | none | v0.5.0 | planned |
| `pdf.metadata.payload` | Text hidden in the file's properties or XMP metadata | C | Info dictionary or XMP packet contains instruction-like or long free text | data or instruction | ATR-2026-00515 (phrase part) | v0.1.0 | partial (Info and XMP length; instruction hook at US-038) |
| `pdf.annotation.hidden` | Text in notes, form fields, tooltips or attachments a person did not open | C | annotation with hidden or no-view flags, form field values, embedded files | data or instruction | none | v0.1.0 | partial (hidden and no-view flags, embedded files; field values without appearance to be written) |
| `pdf.active.content` | The file carries JavaScript or an open action; Paperglass never runs it | C | `/JS`, `/JavaScript`, `/OpenAction`, `/AA` present; the scan stops for that carrier (malware is DEFERRED) | flagged, info | none | v0.1.0 | covered |

## DOCX

| Technique id | Plain language | View, stage | Threshold or mechanism | Class | ATR | Release | Status |
|--------------|----------------|-------------|------------------------|-------|-----|---------|--------|
| `docx.run.vanish` | Text marked hidden in Word | C (self-proving) | `w:vanish` or `w:specVanish` on a run | data or instruction | none | v0.1.0 | planned |
| `docx.run.color` | Text coloured to match the page | C, B stage 1 after conversion | run colour within 24/255 of the page or shading colour | data or instruction | none | v0.1.0 | planned |
| `docx.run.tiny` | Text too small to read | C | run size below 2 pt (`w:sz` below 4) | data or instruction | none | v0.1.0 | planned |
| `docx.part.hidden` | Text in comments, tracked changes, field codes, headers, footers, alt text or document properties | C | the part exists and carries text the body does not; alt text and properties are benign-hidden under length and phrasing constraints | data or instruction; benign-hidden | none | v0.1.0 | planned |

## Any text format

| Technique id | Plain language | View, stage | Threshold or mechanism | Class | ATR | Release | Status |
|--------------|----------------|-------------|------------------------|-------|-----|---------|--------|
| `text.unicode.invisible` | Characters that carry text but draw nothing: tag characters, zero-width joiners, direction overrides, look-alike letters | A normalisation probe (stage 0) | U+E0000 block, U+200B to U+200F, U+202A to U+202E, U+2066 to U+2069, confusables outside the document's script | data or instruction | ATR-2026-00515 (zero-width split part) | v0.1.0 | partial (tags, zero-width, bidi, format characters; confusables to be written) |
| `text.instruction.hint` | Hidden text that reads like an instruction to a model (raises severity only; never a finding on its own) | A, on hidden regions only | phrase pack match or an installed classifier plug-in | modifier | ATR-2026-00515 | v0.1.0 | planned |

## HTML and Markdown (v0.4.0)

| Technique id | Plain language | View, stage | Threshold or mechanism | Class | ATR | Release | Status |
|--------------|----------------|-------------|------------------------|-------|-----|---------|--------|
| `html.dom.hidden` | Text a browser would not show: display none, visibility hidden, aria-hidden, zero size, off-screen | C (DOM and style rules) | computed rule on the element or an ancestor | data or instruction | ATR-2026-00515 (CSS part) | v0.4.0 | planned |
| `html.comment.payload` | Text inside an HTML comment | C | comment node with free text | data or instruction | none | v0.4.0 | planned |
| `html.font.remap` | A web font that draws different letters than the text says | C, stage 3 | `@font-face` with a remapped cmap (arXiv 2505.16957) | structure-only until confirmed | none | v0.5.0 | planned |
| `md.hidden` | Markdown that renders nothing: HTML comments, reference-style definitions, zero-width characters | C, A | comment or unused reference definition with free text | data or instruction | none | v0.4.0 | planned |

## PPTX and images (v0.5.0)

| Technique id | Plain language | View, stage | Threshold or mechanism | Class | ATR | Release | Status |
|--------------|----------------|-------------|------------------------|-------|-----|---------|--------|
| `pptx.slide.hidden` | A slide marked hidden | C | `show="0"` on the slide | data or instruction | none | v0.5.0 | planned |
| `pptx.shape.offslide` | A text box placed outside the slide | C, B stage 1 | shape bbox outside the slide size | data or instruction | none | v0.5.0 | planned |
| `pptx.notes.payload` | Text in speaker notes | C | notes part with text | data or instruction; benign-hidden for short presenter notes | none | v0.5.0 | planned |
| `image.text.low_contrast` | Text inside an image that a person cannot make out | B stage 2 contrast sweep | OCR finds text only after a contrast stretch | data or instruction | none | v0.5.0 | planned |
| `image.metadata.payload` | Text hidden in EXIF or XMP of an image | C | EXIF or XMP field with free text | data or instruction | none | v0.5.0 | planned |

## Benign-hidden allowlist (public, tested, constrained)

| Case | Constraint that keeps it benign | Fixture |
|------|---------------------------------|---------|
| Alt text on images and shapes | at most 300 characters, no instruction-phrase match | `tests/fixtures/benign/alt_text/` |
| ActualText for ligatures and hyphenation | at most 4 characters, replaces a glyph run of the same length | `tests/fixtures/benign/actualtext_ligature/` |
| OCR text layer on a scanned page (Tr 3) | OCR of the render matches the layer above the alignment threshold | `tests/fixtures/benign/ocr_layer/` |
| Tagged-PDF structure and bookmarks | no text that the page does not show | `tests/fixtures/benign/tagged_pdf/` |
| Document properties (title, author) | at most 200 characters, no instruction-phrase match | `tests/fixtures/benign/properties/` |

Anything outside a constraint is not benign-hidden; it is a finding of the technique that hid it.

## Not covered by design (see SCOPE.md DEFERRED)

Semantic injection in visible text; malware, macros and active content (presence flagged, never analysed); image steganography; float-array carriers and any payload with no hidden text and no visual discrepancy; acrostics (COULD).
