# Advisors

Invited in week 1 (US-022) to review the coverage matrix, the benchmark design and two release candidates (v0.3.0 and v1.0.0). Recorded: who, when, what they were asked, what they answered. Nothing is published about a person without their yes.

| Group or person | Invited | Asked to review | Answer |
|-----------------|---------|-----------------|--------|
| PhantomLint authors (Univ. of Melbourne) | week 1 | coverage matrix, benchmark design | pending |
| CrackedPDFs authors (UC Berkeley) | week 1 | benchmark hygiene, split design | pending |
| PhantomText authors (Univ. of Padua) | week 1 | technique list, sample generation | pending |
| Semantic Integrity authors | week 1 | canaries, font and ActualText probes; corpus request | pending |
| One reviewer from OWASP GenAI or the ATR project | week 1 | threat model, ATR scan-target proposal | pending |

## Name check (22 Sep 2026, US-022)

| Where | Result |
|-------|--------|
| PyPI `paperglass` | free (404 on the JSON API) |
| npm `paperglass` | free (404) |
| GitHub organisation `paperglass` | not an organisation; a user account named `paperglass` exists, so the project lives under `SuhaasNv/paperglass` and the alternatives (Glasspaper, Splitview, Twoviews) stay on hold |
| Domain | not checked yet; not needed before v0.4.0 (the REST service uses the Railway host until then) |

## Invitation draft (to send by the owner in week 1)

Subject: Paperglass: an open document trust scanner and benchmark, built on your work

Hello <name>,

I am building Paperglass, an Apache-2.0 scanner that compares what a parser extracts from a document with what a person sees on the rendered page and with the document's structure, and reports every discrepancy with the exact object that caused it. Your <paper or tool> is one of the four pieces of work it is built on, and it is cited in the brief and in the benchmark design.

I would value fifteen minutes of your time at two points: a look at the coverage matrix and the benchmark design now (THREATS.md and docs/08-benchmark/BENCHMARK_DESIGN.md in the repository), and a look at two release candidates later (the benchmark release in week 6 and 1.0 in week 12). If you would rather not, a one-line reply saying so is welcome too, and the credit stays either way.

Specific to you: <PhantomLint: whether the phrase gate can be disabled for a with-and-without comparison; CrackedPDFs: the placement-label erratum and whether a corrected label set exists; PhantomText: nothing needed beyond attribution, the licence is MIT; Semantic Integrity: whether the 25 canaries and the 36 attack documents can be shared for the benchmark, under any licence you choose>.

Repository: https://github.com/SuhaasNv/paperglass

Thank you,
Suhaas

## ATR scan-target proposal (to open as a discussion on the ATR repository in week 1)

Title: Proposal: a document_structure scan target for hiding techniques that have no text form

The registry's current targets (llm_input, mcp_exchange, tool_call, tool_response, skill) express phrase-level rules over extracted text. Hidden-text techniques in user-supplied documents (ATR-2026-00515) mostly have no text form: a text render mode, a ToUnicode remap, a hidden optional content group, a Word vanish run. A document_structure target would let a rule name a mechanism (format, object, property, threshold) rather than a regex, with a reference implementation that any scanner can be checked against. Paperglass offers to be that reference implementation and to submit one YAML per technique once the target exists. Draft schema and the technique list: THREATS.md in the repository.
