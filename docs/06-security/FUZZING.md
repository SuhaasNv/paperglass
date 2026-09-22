# Fuzzing

## Corpus

`tests/fuzz/corpus/<format>/`: malformed files collected from public crashers (pdfium, qpdf, python-docx issue trackers), mutations of the fixtures, and every crasher found by hypothesis. Each file has a one-line note in `tests/fuzz/corpus/INDEX.md`: source, what it breaks, the date it was added.

## Strategies

`tests/fuzz/test_fuzz.py`: hypothesis strategies that mutate fixtures (byte flips, truncation, object number swaps, xref corruption, zip entry renames) and assert the sandbox returns a report with a `parse.failure` finding, within the time limit, without an exception.

## Running

Built at US-021 (22 Sep 2026). `uv run pytest tests/fuzz -q` runs the corpus (12 files) and three hypothesis strategies (byte replacement, truncation, random bytes) with `PAPERGLASS_FUZZ_EXAMPLES` examples each (15 by default; CI uses the same; a nightly run with more examples is a follow-up). Everything goes through `build_pages` and every registered detector; the assertion is that nothing raises.

## Adding a crasher

1. Reproduce with `paperglass scan --tier fast <file>`; note the exception or hang.
2. Copy the file to `tests/fuzz/corpus/<format>/<short-name>.<ext>` and add the INDEX line.
3. Fix the parser wrapper or the sandbox so the result is a `parse.failure` finding.
4. The corpus test now covers it forever.

Security-relevant crashers (anything that escapes the sandbox) go through `SECURITY.md`, not a public issue.
