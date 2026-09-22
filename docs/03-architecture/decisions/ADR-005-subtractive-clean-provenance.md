# ADR-005: Subtractive clean() with provenance tags and a fidelity number

Date 22 Sep 2026. Status: accepted, not yet built (US-064).

## Context
The brief (UC2 sanitise) said clean() returns "what OCR of the rendered page confirms". A RAG developer's objection: OCR text is worse than pdfplumber's for a clean invoice (tables, headings, footnotes lost). Security-Fidelity Tradeoffs (ICML 2026) found no defence achieved both security and fidelity; the most secure lost 26 to 29 percent of task fidelity by suppressing benign text.

## Constraints
Keep the caller's structure; remove only what was proven hidden; benign-hidden preserved and labelled; the result composable with model-side defences.

## Options considered
### Option A: subtractive: caller's text minus confirmed-invisible runs, every run tagged, fidelity reported
- Pros: fidelity provable (target 99.9 percent benign words retained); provenance tags let spotlighting or taint tracking act only on unconfirmed runs; works with any extractor.
- Cons: needs the run-level alignment between the caller's text and View A; when the caller's extractor is not ours, alignment is fuzzy.
### Option B: substitutive: OCR-confirmed text in reading order
- Pros: nothing hidden can survive.
- Cons: loses structure and small text; OCR errors become the pipeline's text; the ICML result in practice.

## Decision
Option A, with substitution available behind an explicit flag.

## Rationale
The pipeline should keep the honest part of every document, and be able to prove how much it kept.

## Consequences
### Positive
Fidelity becomes a benchmark column; the sanitiser is a differentiator, not a liability.
### Negative
Alignment to a foreign extractor is approximate; the fidelity number is reported per document so the caller can decide.

## Validation
Fidelity on the benign corpus in `BENCHMARK.md`; golden files for `CleanResult`.
