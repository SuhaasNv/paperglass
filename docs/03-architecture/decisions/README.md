# Architecture decision records

Seven decisions so far, each in the same shape: Context, Constraints, Options with pros and cons, Decision, Rationale, Consequences (positive, negative), Validation, and dated amendments as the code changes. Each line below is the decision in one breath: chose X over Y because Z.

| ADR | Chose | Over | Because |
|-----|-------|------|---------|
| [001 Apache-2.0 and permissive dependencies](ADR-001-apache-2-permissive-dependencies.md) | Apache-2.0 for code, CC BY 4.0 for the benchmark, MIT/BSD/Apache/MPL dependencies only, DCO | GPL or AGPL, or a gated model in core | A scanner that sits in every upload pipeline must be adoptable by companies and by other open tools without a licence conversation |
| [002 pypdfium2, not PyMuPDF](ADR-002-pypdfium2-not-pymupdf.md) | pypdfium2 for rendering and default extraction, pikepdf and fontTools for structure | PyMuPDF | PyMuPDF is AGPL and would force AGPL or a commercial licence on every user; pdfium is what most viewers use, so View B matches what people see |
| [003 Three views as a cascade](ADR-003-three-views-cascade.md) | View A, a View B cascade (ink check, OCR on crops, glyph arbiter, deep full-page), View C, with findings promoted from possible to confirmed | Two views with full-page OCR (PhantomLint), or structure rules alone (Semantic Integrity scanner) | Full-page OCR cannot meet 300 ms; structure alone has published benign hit rates up to 6.81 percent; the cascade is fast, and confirmation is what makes the false-positive target reachable |
| [004 Verdict without a score](ADR-004-verdict-without-score.md) | Four verdicts plus severity counts, from confirmed findings only | A 0 to 100 trust score | A number invites ranking people and contradicts "never decides an outcome for a person"; findings say everything the number would |
| [005 Subtractive clean with provenance](ADR-005-subtractive-clean-provenance.md) | Remove only confirmed-invisible runs from the caller's own text; tag every run; report fidelity | Replace the text with OCR-confirmed text | Text-suppressing defences lose 26 to 29 percent fidelity (ICML 2026); a sanitiser that provably removes only invisible text can claim both security and fidelity, and provenance tags compose with model-side defences |
| [006 Delivery pipeline](ADR-006-delivery-pipeline.md) | `main` sacred and default, `dev` integration, story branches, `--no-ff`, release by pull request and tag, PyPI trusted publishing, GHCR images by tag, Railway development and production with an approval gate | Trunk-based on `main`, or Railway building from the repository | One maintainer needs a history that reads story by story and a production that a green CI on a weekend cannot change; the tested artefact is the deployed artefact |

## Amendments as built

None yet.
| [007 The report carries its pages](ADR-007-pages-in-the-report.md) | `pages` in the report: thumbnail, every run with a box and a status | Recomputing the diff from the file, or full-page OCR | The web app never keeps the file, so the report must carry what the diff needs; the ink check already classifies every run |
