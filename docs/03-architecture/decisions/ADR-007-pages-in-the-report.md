# ADR-007: The report carries its pages

Date 22 Sep 2026. Status: accepted (US-043).

## Context
The word-aligned diff (what the model reads beside what a person sees, every unmatched run marked) is the centrepiece of the report and the web app. The file is never stored by the web app, so the report must carry whatever the diff needs.

## Constraints
No file storage; a report that opens offline; deterministic output; a JSON size a browser and PostgreSQL row are comfortable with; `--redact` must still produce a report that carries the least content.

## Options considered
### Option A: `pages` in the report: size, a JPEG thumbnail of the rendered page, every extracted run with its box and a status
- Pros: one artefact carries the whole diff; the same rule (stage 1 ink check) classifies runs and findings; the web app and the HTML file read the same data.
- Cons: schema bump to 2; reports grow by roughly 60 to 120 KB per page; goldens regenerate.
### Option B: recompute the diff on demand from the file
- Pros: smaller reports.
- Cons: the web app has no file (it is scanned in memory and discarded), so the diff would need the file uploaded again, and an HTML report could not carry it at all.
### Option C: full-page OCR text as the right column
- Pros: a text-to-text diff.
- Cons: full-page OCR is the deep tier by contract (never default); the ink check already answers the question the diff asks.

## Decision
Option A. Thumbnails at most 720 px wide, JPEG quality 72, at most 20 per report; runs classified `visible`, `hidden`, `benign-hidden` or `unverified`; `--redact` drops thumbnails and shortens runs; a v2 reader accepts a v1 report.

## Rationale
The diff is a fact about the document that the report should carry, like the crops; the reader must not have to trust the file being available later.

## Consequences
- Positive: the web app's "Under the glass" and the HTML report show the real page with the model's text in place; old v1 reports in the database still open (no pages, crops only).
- Negative: larger reports; a page cap; DOCX and text have no thumbnail until a converter lands.

## Validation
`tests/unit/test_pageviews.py`, the regenerated goldens, `tests/unit/test_schema.py` (v1 accepted), and the frontend and report tests that render the pages.
