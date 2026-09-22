# The problem: the human sees one document, the model reads another

## Statement

Every AI system that reads uploaded files trusts an extraction layer. That layer often returns text a person never sees: white-on-white text, 2 pt fonts, off-page text, invisible render modes, Unicode tag characters, remapped fonts, ActualText overrides, hidden Word runs, comments, metadata. The model obeys what it reads; the reviewer approves what they see. Attacks live in the gap, and so do honest mistakes (an OCR layer that drifted, a template's leftover placeholder).

## Evidence (verified 22 Sep 2026; full citations in the brief, section 16)

- About 1 percent of roughly 200,000 real resumes carried hidden injections; the count rose sevenfold between July 2024 and November 2025; more than 90 percent of the injected text was hidden data, not instructions (USENIX Security 2026). ManpowerGroup finds hidden text in about 100,000 resumes a year.
- 18 arXiv manuscripts carried hidden reviewer prompts (July 2025); 2026 benchmarks show the trick still works on LLM reviewers.
- Every one of 16 PDF stacks tested exposed at least one of 25 extraction gaps; PDFium exposed 22 (Semantic Integrity, June 2026).
- PhantomText reached 74.4 percent success across 357 scenarios against five data loaders with 19 hiding techniques.
- EchoLeak (CVE-2025-32711) exfiltrated data from Microsoft 365 Copilot with zero clicks through hidden email text.

## Why the obvious fix fails

Phrase classifiers (Prompt Guard, regex rules, embedding matches) look for instructions. Most real injections are not instructions; they are hidden skills, hidden experience, a copy of the job posting. On CrackedPDFs, PromptGuard on extracted text reaches F1 0.39; adding document structure reaches 0.96. A parser flag that strips hidden text (OpenDataLoader) removes the payload silently: no report, no evidence, nothing a reviewer can act on, and nothing for the semantic-override family where the text is not hidden at all, the model simply reads different letters than the page draws.

## What would solve it

A scanner that answers one question with evidence: would a human reviewer have seen everything the model is about to read? It needs three views (extracted, rendered, structural), a finding that names the mechanism and can be reproduced from the bytes, a verdict that never rests on a phrase, a sanitiser that removes only what was proven hidden, and a public benchmark so the claim can be checked by anyone. The durable property: to get past the rendered view the attacker has to make the text visible, which defeats the attack.

## What it must not become

A tool that ranks people. Paperglass never decides an outcome; it says what was hidden, where, and how, in words a reviewer can check. Report copy says "hidden text found", never "fraud".
