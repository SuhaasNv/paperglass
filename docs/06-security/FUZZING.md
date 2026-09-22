# Fuzzing

## Corpus

`tests/fuzz/corpus/<format>/`: malformed files collected from public crashers (pdfium, qpdf, python-docx issue trackers), mutations of the fixtures, and every crasher found by hypothesis. Each file has a one-line note in `tests/fuzz/corpus/INDEX.md`: source, what it breaks, the date it was added.

## Strategies

`tests/fuzz/test_hypothesis.py`: hypothesis strategies that mutate fixtures (byte flips, truncation, object number swaps, xref corruption, zip entry renames) and assert the sandbox returns a report with a `parse.failure` finding, within the time limit, without an exception.

## Running

`uv run pytest tests/fuzz -q` (CI runs the corpus on every push; the hypothesis run uses a fixed seed in CI and a random seed nightly, US-021).

## Adding a crasher

1. Reproduce with `paperglass scan --tier fast <file>`; note the exception or hang.
2. Copy the file to `tests/fuzz/corpus/<format>/<short-name>.<ext>` and add the INDEX line.
3. Fix the parser wrapper or the sandbox so the result is a `parse.failure` finding.
4. The corpus test now covers it forever.

Security-relevant crashers (anything that escapes the sandbox) go through `SECURITY.md`, not a public issue.
