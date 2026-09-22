# False-positive log

A false-positive report is answered before feature work. Each entry: the issue, the document (or a description if it cannot be shared), the technique that fired, why it fired, the fix (threshold, constraint, detector), and the fixture under `tests/fixtures/false-positives/<issue>/` that now guards it. Credit in `CONTRIBUTORS.md`.

| Date | Issue | Technique | Why it fired | Fix | Fixture |
|------|-------|-----------|--------------|-----|---------|
| none yet | | | | | |

## 22 Sep 2026: the PhantomLint clean documents (first run on real files)

Found by `paperglass bench run --corpus v1 --detector paperglass --tier fast` on the six clean documents in PhantomLint's `tests/good` (real arXiv papers and CVs): every one came back `suspicious`. Recorded here before any fix, per the standing rule that a false positive is answered before feature work.

| Document | What fired | Why it is a false positive | Fix |
|----------|------------|----------------------------|-----|
| `alexander-fenster.pdf`, `2006.03257v1.pdf` (pdfTeX) | `pdf.metadata.payload`, confirmed, medium: Info key `/PTEX.Fullbanner`, 85 to 92 characters | the pdfTeX banner is tool provenance, present in most arXiv papers; nothing a model would read as an instruction | known producer keys (`PTEX.*`, `Producer`, `Creator`, `CreationDate`, `ModDate`, `Trapped`, `GTS_*`) are never payload; a non-standard key is a finding only when its value is long and free text |
| `jon-hobbs-smith-cv.pdf` | `pdf.text.covered`, confirmed, medium, 822 findings, one per `'` or `-` glyph | punctuation glyphs whose ink falls outside the extractor's box; no information content; 105 s spent promoting them | a run must carry at least three word characters before the ink check can confirm it hidden; the same guard for `pdf.text.low_contrast` at stage 1 |
| `2006.03257v1.pdf` (LaTeX fonts) | `pdf.font.tounicode_mismatch`, possible, info, 50 findings: code 0x1b draws the ligature `ﬀ` and ToUnicode says `ff` | that is what ToUnicode is for; the two are the same text under compatibility normalisation | compare the glyph's text and the ToUnicode text after NFKC normalisation; a match is not a finding |
| every pdfTeX paper | `pdf.active.content`, confirmed, info: `/OpenAction` present | pdfTeX writes an `/OpenAction` that only sets the initial view (`/Fit`); nothing runs | `/OpenAction` is flagged only when its action is JavaScript, Launch, SubmitForm, ImportData, GoToR or URI; a plain GoTo view is not active content |

Fixtures under `tests/fixtures/benign/` guard each case once fixed; the v1 results file is re-run and the numbers here replaced by the new ones.
