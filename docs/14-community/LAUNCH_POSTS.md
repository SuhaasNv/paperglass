# Launch posts (drafts, US-045)

Drafted 22 Sep 2026 for the v0.2.0 moment. The owner posts; nothing here goes out by itself. Copy rules apply: no em dashes, no emoji, "hidden text found" and never "fraud" or "cheating"; every number names its source.

## Show HN

Title: Show HN: Paperglass, see exactly what the model reads in a PDF or DOCX

Body:

Paperglass is an open-source (Apache-2.0) document trust scanner. It extracts the text a model would receive, renders the page a person would see, reads the document's structure, and reports every place the three disagree: technique, page, the hidden text, the rendered crop, the exact PDF object or Word run that hid it, and a one-line command that prints those bytes so you never have to trust the tool.

Why: resume screeners, peer-review assistants and RAG pipelines read files through an extraction layer nobody looks at. White-on-white text, 2 pt text, text on a switched-off layer, a font whose ToUnicode map says different letters than it draws, a Word run marked hidden: the model reads it, the person never sees it. About 1 percent of real resumes carry hidden injections, and most of them are hidden data (skills, the job posting itself) rather than orders, which is why phrase classifiers miss them (numbers and sources in the project brief, section 2).

What it is not: it does not judge visible text, does not detect malware, and gives no score. The verdict is one of four words with counts and evidence. Hidden is not always malicious: alt text, ligature ActualText, OCR layers on scans are reported as benign-hidden, never as an attack.

Try it: `pip install paperglass`, then `paperglass scan resume.pdf`, or the web app (files are scanned in memory and never stored; the report lives 7 days under an unguessable link). Eighteen techniques for PDF, DOCX and text, each with a positive and a negative fixture; a `fingerprint` command tells you which of your installed extractors hand the hidden text to a model.

The one claim: to get past it, an attacker has to make the text visible, which is the one thing the attack cannot afford.

Links: repository, the 30-second demo, THREATS.md (the coverage matrix with thresholds and known gaps), SECURITY.md.

## OWASP GenAI Security Project (Slack, document and RAG channels)

Short version:

Sharing Paperglass, an open-source scanner for the "what the model reads versus what the person sees" gap in uploaded documents. Three views (extracted text, rendered page, structure), findings promoted from possible to confirmed only when the render agrees, a verdict with evidence and no score. Eighteen techniques today (PDF colour, size, off-page, render modes, opacity, layers, covered text, ToUnicode and ActualText, metadata, annotations, active content; DOCX hidden runs, colours, sizes, hidden parts; invisible Unicode). The registry maps to ATR-2026-00515 where a phrase-level rule fits, and the project proposes a document-structure scan target for ATR (docs/14-community/ADVISORS.md). Feedback on the threat matrix and false-positive reports are the most useful thing right now: THREATS.md lists thresholds and gaps by name.

## docling-parse: a pull request, not a comment

Branch name: `feat/paperglass-hidden-text-step`. Title: Optional hidden-text check before parsing, backed by Paperglass.

Description:

Issue 134 asked for a way to know when extracted text is not what a reader sees. This pull request adds an optional, off-by-default pipeline step that runs Paperglass (Apache-2.0, offline, no telemetry) on the input and attaches `paperglass.verdict`, `paperglass.severity_counts` and the finding ids to the document metadata; a `policy` option can drop confirmed-invisible runs before parsing. Nothing changes when the option is off. Tests use the fixtures Paperglass ships (a positive and a negative per technique). Happy to move the step into a separate package if that fits the project better; the adapter contract is documented in docs/11-integrations/DOCLING.md.

(To be opened at v0.4.0 when the Docling adapter exists; drafted here so the v0.2.0 posts can point at it.)
