# ADR-003: Three views, with View B as a cascade and findings promoted from possible to confirmed

Date 22 Sep 2026. Status: accepted, not yet built (US-030, US-031, US-087).

## Context
The brief (section 9) described three view builders followed by a discrepancy engine, with a standard tier under 300 ms per page. RapidOCR on a full 150 dpi page costs 0.5 to 2 s on CPU. The Semantic Integrity paper reports benign hit rates up to 6.81 percent for font-decoding checks and up to 3.08 percent for reading-order checks; the brief's overall false-positive target is 0.1 percent. UNITES shows a four-rule visual cascade is 18 times faster and 134 times cheaper than a vision model at a small precision cost.

## Constraints
Standard tier p50 at or below 300 ms on a 4-core CPU. Verdict-driving false positives at or below 0.1 percent. The semantic-override family (ToUnicode, ActualText) must be reachable.

## Options considered
### Option A: View A, View B as a cascade (raster ink check, OCR on crops, glyph arbiter, deep full-page OCR), View C; candidates promoted possible to confirmed
- Pros: stage 1 catches most hiding techniques in milliseconds with no OCR; OCR cost is proportional to suspect runs, not pages; structure-only findings stay informational so the false-positive target is reachable; the glyph arbiter makes the semantic-override family real.
- Cons: more stages to test; two confidence levels to explain in the report.
### Option B: two views with full-page OCR (PhantomLint's shape)
- Pros: simple, proven.
- Cons: 43 to 68 s per document in PhantomLint; no structure, so no semantic overrides; OCR noise is the main false-positive source.
### Option C: structure rules only (Semantic Integrity scanner's shape)
- Pros: milliseconds.
- Cons: the paper itself calls it triage; benign hit rates make it unusable as a verdict source.

## Decision
Option A, as specified in `../VIEWS.md`. Tiers are named by stage: fast (0, 1), standard (plus 2, 3), deep (plus 4).

## Rationale
Detect the mechanism, confirm it on the raster, and never let an unconfirmed structural hint drive a verdict.

## Consequences
### Positive
Honest speed budgets; a false-positive target that can be met; a report that says whether each finding was confirmed and which pages were render-verified.
### Negative
Stage 3 is the hardest code in the project and lands in v0.5.0; until then ToUnicode and ActualText findings are informational.

## Validation
Latency per stage in `BENCHMARK.md`; per-technique false positives on the benign corpus split by verdict-driving and informational; the 25 canaries at v0.5.0.
