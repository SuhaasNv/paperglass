# Personas

| Persona | Situation | What they need from Paperglass | Use case |
|---------|-----------|--------------------------------|----------|
| Developer shipping RAG or an agent | Ingests files from strangers automatically; cannot block every suspicious file, cannot read the invisible layer | A drop-in step: verdict and severity counts in metadata, a subtractive clean text with provenance tags, a table of which parsers are fooled (`fingerprint`), under 300 ms a page | UC1, UC4 |
| Security engineer | Owns the upload boundary; distrusts scanners, trusts bytes | The mechanism (exact object) and a reproduce command per finding; a hardened image; a threat model; a fuzz corpus; ATR ids | UC1, UC4 |
| Reviewer (recruiter, editor, loan or licensing officer) | Signs the decision; must see the trick, not a JSON file | One offline HTML file: the page, the highlighted region, the hidden text beside it, a plain sentence per technique, no score to rank by | UC2 |
| Researcher or detector maintainer | Wants comparable numbers | One corpus, one harness, a two-function adapter, per-technique and per-family recall, false positives split into verdict-driving and informational, fidelity, immutable versions | UC3 |
| Security tester or red teamer | Wants new samples to test their own pipeline | A seeded, deterministic generator with matched controls, one file plus a fixture pair to add a technique, stable technique ids | UC5 |
| The person whose document is scanned | Wrote a resume or a manuscript | Their data does not spread: `--redact`, no telemetry, no content in logs, no real documents in fixtures, report copy that never calls them a cheat | every use case |
