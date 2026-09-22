# Paperglass

See exactly what the model reads.

Paperglass is an open-source document trust scanner and benchmark for AI pipelines. It shows the text a document gives to a model, compares it with the page it shows to a person and with the document's structure, and reports every place the three differ: technique, page, bounding box, the hidden text, the rendered crop, the exact object that hid it, and a command to reproduce the finding without trusting Paperglass.

To get past Paperglass an attacker has to make the text visible, which is the one thing the attack cannot afford.

**Status (22 Sep 2026):** planning complete, no code yet. First release v0.1.0 (UC1 Scan and Verdict) is planned for week 4. This README describes what will exist at each release and is rewritten as each ships; nothing below is a claim about working software until the release section says so.

## The problem

Resume screeners, RAG chatbots, peer-review assistants and coding agents read uploaded files through an extraction layer a person never sees. About 1 percent of real resumes carry hidden injections, and more than 90 percent of them are hidden data (skills, experience, the job posting itself) rather than instructions, which is why phrase-based classifiers miss most of them. Every PDF stack tested in 2026 exposed at least one of 25 known extraction gaps. The model obeys what it reads; the human approves what they see. The attack lives in the gap. Sources and numbers: `docs/00-brief/PROJECT_BRIEF.md`, section 2.

## How it works

Three views, one verdict. View A is what extractors return (pluggable; the report names the extractor). View B is what a person sees: the page rendered, every extracted run checked for ink on the raster, then OCR on the suspect crops. View C is structure: render modes, colours, sizes, clipping, layers, ActualText, ToUnicode maps, fonts, OOXML parts, DOM styles. A candidate from View C is `possible` until View B or a self-proving mechanism confirms it; the verdict (`clean`, `benign-hidden`, `suspicious`, `malicious`) comes from confirmed findings only. Details: `docs/03-architecture/VIEWS.md`.

## 60-second demo (v0.2.0)

To be written when v0.2.0 ships: `paperglass scan resume.pdf`, the hidden sentence, `paperglass report`, the side-by-side diff, `paperglass fingerprint`, `paperglass clean`. Script: `docs/13-demo/DEMO_SCRIPT.md`.

## Install (v0.1.0)

To be written when v0.1.0 ships. Planned: `pip install paperglass` gives the fast tier with no binary dependencies; `pip install "paperglass[ocr]"` adds View B.

## CLI (v0.1.0)

Planned commands: `paperglass scan`, `paperglass fingerprint`, `paperglass show --object`, `paperglass report` (v0.2.0), `paperglass clean` (v0.4.0), `paperglass bench` (v0.3.0). Exit codes 0 clean, 1 suspicious, 2 malicious, 3 error. Contract: `docs/04-report-design/CLI_DESIGN.md`.

## Python API, adapters, MCP, REST

Planned for v0.1.0 (API) and v0.4.0 (LangChain, LlamaIndex, Docling, GitHub Action, MCP, REST). One page per adapter: `docs/11-integrations/`.

## Benchmark (v0.3.0)

Numbers appear in `BENCHMARK.md` only with the corpus, the version and the one command that reproduces them from a clean clone. Design: `docs/08-benchmark/BENCHMARK_DESIGN.md`.

## Security

Every input is untrusted. Every parser call runs in a sandboxed subprocess with CPU, memory and time limits; the scanner never executes document content and makes no network call unless asked. Disclosure: `SECURITY.md`. Threat model: `docs/06-security/THREAT_MODEL.md`.

## Scope, roadmap, board

What is built, deferred and why: `SCOPE.md`. Twelve weeks, one release per use case: `docs/05-planning/ROADMAP.md`. Stories, mirrored from the Notion board: `docs/05-planning/ISSUES.md`. Documentation index: `docs/README.md`.

## AI usage

Built with AI assistants under standing instructions checked into this repository (`CLAUDE.md`). Every generated detector ships with a fixture pair and its false-positive rate in the pull request. Full record: `AI_USAGE.md`.

## What I would do next

To be written at each release. Known limits today are listed in `SCOPE.md` under DEFERRED.

## Licence

Apache-2.0 for code; CC BY 4.0 for the benchmark corpus index; DCO sign-off for contributions. Third-party licences: `THIRD_PARTY.md`.
