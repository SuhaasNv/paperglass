# Fixtures

```
tests/fixtures/
  pdf/<technique_id>/positive.pdf        one finding of the technique, confidence above 0.9
  pdf/<technique_id>/negative.pdf        the matched control, no finding
  docx/<technique_id>/positive.docx | negative.docx
  html/, md/, pptx/, png/                from the releases that add them
  benign/<case>/*.pdf|docx               yield benign-hidden only (alt text, ligature ActualText, OCR layer, tagged PDF, properties)
  false-positives/<issue-number>/*       real, redistributable documents that were wrongly flagged; yield clean; credited in CONTRIBUTORS.md
  fuzz/ is under tests/fuzz/corpus/
```

Rules:
- Generated fixtures come from the Red Kit with the seed in the file name (`pdf.text.tiny-7-positive.pdf`); hand-made fixtures carry a `SOURCE.md` beside them with how they were made.
- Never a real resume, manuscript or any document with personal data; benign real documents come from public-domain or CC BY sources named in `SOURCE.md`.
- A fixture is small (under 200 KB) and single-purpose; one technique per positive.
- Every fixture has a golden JSON report under `tests/golden/`.
- Adding a fixture: `CONTRIBUTING.md`, "Add a sample".
