# The three views and the discrepancy engine

Written 22 Sep 2026 from the brief and the method sections of PhantomLint, CrackedPDFs, UNITES and Semantic Integrity. Amended as built.

## The one question

Would a human reviewer have seen everything the model is about to read? Three views answer it, and a discrepancy between them is the signal. Instruction-like phrasing only raises severity; it is never the reason for a finding.

## View A: what extractors return

Positioned text runs: text, bbox, font reference, content-stream offset (PDF) or part and run index (OOXML). The backend is pluggable: pypdfium2 by default; pdfplumber, pypdf and pdfminer.six always available; Docling and OpenDataLoader when importable. The report names the extractor. `paperglass fingerprint` runs stages 0 and 1 per backend and prints which backends return each invisible run, because the victim pipeline's parser may not be ours and 9 to 22 of 25 known gaps depend on the parser.

## View B: what a person sees, as a cascade

Render once per page with pypdfium2 at 150 dpi, or 200 dpi when any font on the page is under 6 pt; the dpi is in the report.

- Stage 1, ink check, no OCR. For every extracted run, sample the raster inside its bbox: ink density (threshold 1.5 percent), contrast against the local background (24/255), pixel variance, bbox inside the media box and the current clip. Classify visible, invisible, uncertain. This alone catches white-on-white, render modes 3 and 7, tiny text, near-zero alpha, off-page, clipped, OCG-off and covered-by-shape, with the stage 0 mechanism attached. Milliseconds. This is the fast tier, and it is why 100 ms per page is honest.
- Stage 2, OCR on crops only. Invisible runs get an OCR crop for the evidence pair and to catch text that is visible under a covering shape; uncertain runs get OCR plus rapidfuzz alignment with per-font-size thresholds tuned on the benign corpus, OCR-uncertain characters masked (PhantomLint's only false positives were OCR noise beside real text). Tens of milliseconds on a typical page.
- Stage 3, glyph verification (v0.5.0). For a suspect font, render each glyph from the embedded program, render the declared character in a reference font, compare shapes (perceptual hash or SSIM), confidence by mismatch fraction, cache per font hash. ActualText spans are OCRed alone and compared. This is the semantic-override family: no hidden text, the model reads different letters than the page draws.
- Stage 4, deep, opt-in. Full-page OCR aligned to View A to confirm reading-order and font-decoding families; optional small vision model for scans. Seconds per page.

Full-page OCR is never in the standard tier; on CPU it costs 0.5 to 2 s a page and would make the 300 ms budget a lie.

## View C: structure

Probes per format emit candidates with a named mechanism and, where possible, a reproduce command:

- PDF: text render mode, fill colour and alpha, ExtGState, clip path, optional content group state, MediaBox and CropBox, `/ActualText`, ToUnicode CMaps and font descriptors (Type 3, CID, missing ToUnicode), annotations and form fields, embedded files, `/JS` and `/OpenAction` (flag and stop), Info and XMP.
- DOCX: `w:vanish`, run colour and shading, `w:sz`, comments, tracked changes, field codes, headers and footers, alt text, document properties.
- HTML and Markdown (v0.4.0): display none, visibility hidden, aria-hidden, zero size, off-screen positioning, comments, unused reference definitions; web-font remapping (v0.5.0).
- PPTX and images (v0.5.0): hidden slides, off-slide shapes, notes, EXIF and XMP.

Self-proving mechanisms need no View B confirmation: render mode 3 with extractable text, an OCG in the default OFF array with text, `w:vanish`. Everything else is a candidate.

## The discrepancy engine

1. Every View C candidate starts as `possible`.
2. Stage 1 or 2 evidence (no ink, OCR disagreement) or a self-proving mechanism promotes it to `confirmed`, and the finding gets its crop and its why-hidden sentence.
3. Text that View A returns and stage 1 finds invisible with no View C mechanism becomes a `confirmed` finding of the closest technique (covered, low contrast) with mechanism "raster: no ink".
4. Font-decoding and reading-order candidates stay `possible` and informational unless the deep tier confirms them.
5. Benign-hidden constraints apply (alt text length and phrasing, ActualText length, OCR layer agreement, properties length); a run that satisfies them is `benign-hidden`; a run that violates them is a finding of the technique that hid it.
6. Severity class: instruction addressed to a model (high, critical when it names an action); hidden data injection (medium; high when the hidden text contradicts the visible text or duplicates a supplied job description in the resume profile); benign-hidden (info); structure-only (info).
7. Verdict from confirmed findings only: malicious if any confirmed high or critical; suspicious if any confirmed medium; benign-hidden if only benign-hidden; clean otherwise. Thresholds live in the profile.
8. The report states page count, which pages were render-verified and the dpi, because services silently fall back to text extraction above page thresholds and a receipt must say what was checked.

## clean()

Subtractive. Input: the caller's extractor output (or View A). Remove confirmed-invisible runs only; keep structure; tag every run `visible-confirmed`, `benign-hidden`, `structure-only` or `removed`; report words kept, words removed, fidelity against the rendered page. Never substitutes OCR text unless asked. The provenance tags are what a model-side defence (spotlighting, taint tracking) can consume.

## What View B cannot see, by design

Visible-but-encoded payloads: acrostics, float-array carriers, plain visible instructions. They are named in `SCOPE.md` DEFERRED and belong to classifiers. The durable claim: to get past View B an attacker has to make the text visible, which is the one thing the attack cannot afford.
