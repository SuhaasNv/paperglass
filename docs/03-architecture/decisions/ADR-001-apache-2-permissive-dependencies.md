# ADR-001: Apache-2.0 for code, CC BY 4.0 for the benchmark, permissive dependencies only

Date 22 Sep 2026. Status: accepted, not yet built (US-005).

## Context
Paperglass will sit in front of upload pipelines at companies, inside other open-source tools (LangChain, LlamaIndex, Docling), and in research code. Its benchmark will be redistributed. The brief (section 1, section 10) asks for a permissive licence and no gated model as a hard dependency.

## Constraints
No AGPL anywhere in the dependency tree. No model whose weights need a click-through licence in core. Contributions attributable (DCO).

## Options considered
### Option A: Apache-2.0 code, CC BY 4.0 benchmark, MIT/BSD/Apache/MPL dependencies
- Pros: adoptable by companies and by every open tool in the landscape; patent grant; CC BY lets researchers redistribute the corpus index with attribution.
- Cons: none for adoption; MPL (pikepdf) requires file-level copyleft on modifications to pikepdf itself, which we do not make.
### Option B: AGPL code
- Pros: forces improvements back.
- Cons: excludes most companies and every MIT tool; the same reason PyMuPDF is banned.
### Option C: MIT code
- Pros: simplest.
- Cons: no patent grant; Apache-2.0 is the norm for security tooling that companies vet.

## Decision
Option A. `LICENSE` is Apache-2.0; the benchmark index and Red Kit samples are CC BY 4.0 (samples from other sources keep their own licence, recorded per sample); every dependency is listed with its licence in `THIRD_PARTY.md`; DCO sign-off on contributions; Prompt Guard 2 and vision models are user-installed plug-ins.

## Rationale
The scanner is only useful if it is everywhere the documents are.

## Consequences
### Positive
Nothing to negotiate before adoption; the ATR registry and OWASP tooling can reference it.
### Negative
Cannot use PyMuPDF (fastest PDF library) or gated models; the deep tier is limited to Florence-2 (MIT) and SmolVLM2 (Apache-2.0).

## Validation
`THIRD_PARTY.md` reviewed at every release; `pip-audit` and a licence check in CI (US-004).
