# ADR-004: Four verdicts and severity counts, no 0 to 100 score

Date 22 Sep 2026. Status: accepted (US-020).

## Context
The brief (UC1, section 9) specified a trust score 0 to 100 that saturates per severity class. The brief also says Paperglass never decides an outcome for a person. Recruiters and editors are the readers of the report.

## Constraints
The report must let a reviewer decide with their own eyes; a Policy object must still be able to act.

## Options considered
### Option A: verdict (clean, benign-hidden, suspicious, malicious) plus severity counts, from confirmed findings only
- Pros: nothing to rank by; every value is explainable by pointing at a finding; a Policy acts on the verdict and counts.
- Cons: two documents with the same verdict are not ordered; pipelines that want a scalar must compute their own.
### Option B: the saturating score
- Pros: one number for dashboards.
- Cons: a number invites "sort candidates by trust"; saturation rules are opaque; the number adds nothing the findings do not say.

## Decision
Option A. No score field in the schema. Severity classes and escalation rules are documented in `../FINDING_SCHEMA.md`.

## Rationale
A scanner that scores people becomes a tool for ranking them; the verdict is advice with evidence.

## Consequences
### Positive
Simpler schema; the report's top line is a word and a set of counts.
### Negative
The brief's section 9 paragraph on the trust score is superseded (revision note); adapters expose `severity_counts` instead.

## Validation
`tests/unit/engine/test_verdict.py`; the profile file holds the thresholds; copy test that the report never prints a score.
