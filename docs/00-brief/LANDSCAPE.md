# Landscape (verified 22 Sep 2026)

Every project and paper that overlaps with Paperglass, checked on the date above. Star counts and licences are as shown that day. This table is re-verified before each release announcement; a stale row is a bug.

## Open tools

| Project | Licence, stars | What it does | Where it stops | Source |
|---------|----------------|--------------|----------------|--------|
| PhantomLint (Univ. of Melbourne) | BSD-3, 4 | Finds suspicious phrases with MiniLM against a prompt list, renders and OCRs those spans only, diffs. PDF and HTML. 0.092 percent false positives on 3,402 real documents, measured after the phrase gate. | Phrase-gated: recall on hidden data injection unmeasured; 43 to 68 s per document; two views, no structure; PyMuPDF (AGPL), Tesseract, Poppler; output is two text files; bounding-box accuracy named as its main failure by its authors | github.com/tobycmurray/phantom-lint, arXiv 2508.17884 |
| CrackedPDFs (UC Berkeley) | MIT, 2 | 29,322 synthetic PDFs (9,774 injected) from 14 templates; hybrid detector F1 0.960; the benchmark hygiene recipe (provenance split, confounders, label shuffle, shortcut audit) to copy | Synthetic, single page, PDF only, no OCR; erratum (Sep 2026): placement labels record requested not actual position and nearly all payloads sit off-page bottom-left, so F1 here mostly measures off-page detection | github.com/volkthienpreecha/crackedpdfs, arXiv 2607.19396 |
| PhantomText toolkit (Univ. of Padua) | MIT, 5 | 19 hiding techniques for DOCX, HTML, PDF; FileScanner and FileSanitizer | Attack side first; per-technique heuristics; no benchmark, no integrations | github.com/pajola/PhantomText, arXiv 2507.05093 |
| Semantic Integrity static scanner (Liu, Ming) | research artefact | Rules for 25 extraction gaps; 25 canaries and 36 attack documents; benign hit rates published: font-decoding 0.24 to 6.81 percent, reading-order 0 to 3.08 percent on real PDFs | No package, no public corpus (by request); the paper itself calls static scanning "intake triage" needing render or extract confirmation | arXiv 2606.15020 |
| UNITES resume detectors (USENIX 2026) | code released | HCD (four visual rules plus LLM verification of flagged excerpts, 86.1 percent precision, 18x faster and 134x cheaper than the VLM path); VDA (VLM compares render with text, 92.7 percent precision, paid). Finding: more than 90 percent of real injections are data, not instructions | Resume-specific; needs an LLM or VLM API; resume data not shareable | github.com/UNITES-Lab/resume-injection-measurement, arXiv 2605.28999 |
| OpenDataLoader PDF | Apache-2.0 (since 2.0), 29.3k | Parser with rendering-mismatch filters on by default (hidden text, off-page, text at or below 1 pt, hidden OCG); multi-process batch; a LangChain package | Strips silently: no report, no evidence, no location; needs a JVM; PDF only; still exposes semantic-override, reading-order and font-decoding gaps | github.com/opendataloader-project/opendataloader-pdf |
| DocFirewall | MIT, 3 | 12 threat classes, many formats (including RTF, legacy Office, ODF, archives), Docling for deep parsing, 15-language phrase packs, LangChain and LlamaIndex hooks | Per-format heuristics, no render cross-check; 0.00 percent false positives on its own 200-document synthetic corpus (the anti-pattern); unnamed maintainers | github.com/doc-firewall/doc-firewall |
| PDF-Prompt-Injection-Toolkit (zhihuiyuze) | MIT, 66 | Red and blue team: six injection methods, seven detectors including extraction discrepancy | No OCR, no benchmark, no integrations | github.com/zhihuiyuze/PDF-Prompt-Injection-Toolkit |
| Hidden-prompt-scanner-for-documents (arkap1502) | small | CLI plus Flask UI | Single author, no benchmark | github.com/arkap1502/Hidden-prompt-scanner-for-documents |
| LLM Guard (Protect AI) | MIT, 3.1k | InvisibleText input scanner among many | Text only; no render, no structure; the tool many developers already have installed | llm-guard docs |
| hidden-text-detector, pdf-injection-scanner, Ghostlayer, rag-injection-scanner, hiddenink | 0 to 16 stars | Useful technique lists; pdf-injection-scanner's author deleted his ML layer after structural rules caught 15 of 15 real traps with zero false positives | Each tests on its own samples; "my detector and my attacker share an imagination" | GitHub, dev.to/andy8647 |

## Commercial

| Product | What it does | Where it stops |
|---------|--------------|----------------|
| Google Model Armor | Screens PDF, DOCX, PPTX, XLSX, CSV, TXT up to 4 MB in the cloud with text classifiers | Nothing on hidden text, rendering or evidence location; online only; no benchmark |
| Azure Prompt Shields | Documents mode; Spotlighting tags untrusted spans so the model distrusts them | A model-side defence: reduces the effect of an injection, does not tell a person that text was hidden; nothing for semantic overrides where the model reads different words |
| Lakera Guard (Check Point, about US$190 million) | Cloud API, text classifiers | Closed, online, no evidence overlay, no reproducible benchmark |

## Papers that set the design

| Paper | What it settles for Paperglass |
|-------|--------------------------------|
| UNITES (arXiv 2605.28999) | Detect the mechanism, never the intent; report data-injection recall separately; the cheap cascade is the product, the VLM is a labeller |
| CrackedPDFs (arXiv 2607.19396) | Structure belongs in the security boundary (PromptGuard on text F1 0.39, structural plus text 0.96); benchmark hygiene recipe |
| Semantic Integrity (arXiv 2606.15020) | Two confidence levels (any versus high-confidence); font-decoding and reading-order are informational by default; dual-view consistency contract |
| Malicious font injection (arXiv 2505.16957) | Glyph shape versus declared Unicode is the semantic-override signal; the HTML web-font twin |
| Security-Fidelity Tradeoffs (ICML 2026, arXiv 2606.30783) | No defence achieved both security and fidelity; text-suppressing defences lost 26 to 29 percent fidelity; benchmark fidelity with recall |
| The Attacker Moves Second (arXiv 2510.09023), Adaptive Attacks Break IPI Defenses (arXiv 2503.00061) | Adaptive attackers beat single-mechanism classifiers; Paperglass is not a classifier and its durable claim is visibility |
| Beyond Pattern Matching (arXiv 2604.18248) | Provenance tags are the composition point with model-side defences |
| Hiding in Plain Floats (arXiv 2606.08403) | Carriers with no hidden text and no visual discrepancy exist; named in DEFERRED |
| Agent Threat Rules registry, ATR-2026-00515 | Seven regex layers over extracted text; the schema has no scan target for document structure; Paperglass proposes one |
| Microsoft, ASCII smuggling (3 Sep 2026) | Up to 2.37 million messages per weekday at peak; invisible Unicode tags are cheap at scale |
