# 03-architecture

How Paperglass is built and why. Written 22 Sep 2026, before code; each document is amended in the same change as the code it describes, with dates. Where the built system differs, the document changes or the difference is recorded in `../12-reviews/PRODUCTION_READINESS_REVIEW.md`.

| Document | What it holds |
|----------|---------------|
| `ARCHITECTURE.md` | The pipeline, the packages, the layering rule and its test, the adapter table |
| `VIEWS.md` | View A, View B as a cascade, View C, and the discrepancy engine that promotes candidates to confirmed |
| `FINDING_SCHEMA.md` | The Finding and Report models, verdicts, severity classes, schema versioning |
| `TECHNIQUE_REGISTRY.md` | Technique id naming, the `@technique` contract, the plain-language source, severity rules |
| `SANDBOX.md` | Limits, subprocess model, failure findings, what is never executed |
| `decisions/` | ADRs; the index reads "chose X over Y because Z" |
| `diagrams/` | Pipeline, layering and benchmark flow, generated from their sources |

Start with `VIEWS.md`, then `FINDING_SCHEMA.md`. Related: `../02-requirements/`, `../06-security/THREAT_MODEL.md`.
