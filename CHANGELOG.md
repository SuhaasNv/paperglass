# Changelog

All notable milestones. One section per weekly close plus in-week milestones. Story ids refer to `docs/05-planning/ISSUES.md`. Release sections are written in the users' words before the tag.

## v0.1.0 (unreleased): UC1 Scan and Verdict

What you get: `pip install paperglass`, then `paperglass scan file.pdf` (or a `.docx`, `.txt`, `.md`, or a whole directory) prints a verdict of clean, benign-hidden, suspicious or malicious, with every finding's technique in plain words, the page and region, the hidden text, the exact object that hid it, and a `paperglass show` command that prints those bytes so you can check without trusting the tool. `paperglass fingerprint` tells you which of your installed PDF extractors would hand the hidden text to a model. The Python API (`paperglass.scan`, `paperglass.fingerprint`) returns the same as typed models with a versioned JSON schema.

New: 18 detection techniques for PDF, DOCX and plain text, each with a positive and a negative fixture (`THREATS.md`); a three-view pipeline where structure finds candidates and the rendered page confirms them; a sandboxed worker with memory and time limits so a malicious file becomes a finding, not a crash; exit codes for shell pipelines; `--redact` for reports you keep; no telemetry.

Known limits: ToUnicode, ActualText and undecodable-font findings are informational until the glyph arbiter (v0.5.0); DOCX has no rendered view yet; OCR (the standard tier) needs `pip install "paperglass[ocr]"`; speed is measured on a laptop, not the 4-core Linux target; Windows enforces the wall clock but not CPU or memory caps. Nothing here decides anything about a person: the verdict is advice with evidence.

## Week 1 (22 to 28 Sep 2026)

Closed early on 22 Sep 2026 with the v0.1.0 code complete on `dev`; the release itself waits for the owner (PyPI trusted publishing, the pull request to `main`, the tag).

### Shipped

| Story | Outcome |
|-------|---------|
| US-000 to US-006 | Skeleton, schema v1 with golden files, registry and the THREATS.md contract test, sandbox and guards, CI on three operating systems (12 jobs green), governance files, View A with four PDF extractors |
| US-007 to US-018, US-024 | View C for PDF; ten detectors with fixture pairs; mechanism and reproduce on every candidate |
| US-020, US-021, US-030 to US-034 | Verdict rules and profile file, fuzz corpus, View B cascade, discrepancy engine, covered text, static font probes, DOCX views and four detectors |
| US-023, US-025, US-036, US-038 | Fingerprint, redact and no telemetry, the CLI with a long-lived sandbox worker (fast tier 18 ms p50), the instruction-likeness plug-in hook |
| US-005, US-022 (part) | Licence, security policy, code of conduct, contributing recipes, contributors file; name check done; advisor invitations drafted |

Numbers at close: 251 tests (250 passed, 1 skipped on macOS), coverage 92 percent including the sandboxed children; 18 techniques, 36 fixtures; every commit conventional, every story on its own branch merged with `--no-ff`; CI green on `dev`.

### Slipped

- US-019 (fixtures from PhantomText and CrackedPDFs): the generated fixtures covered every technique, and the external corpora belong with the benchmark; moved to week 5 with the corpus index (US-050). Board note added.
- US-022 (advisor invitations): drafts written; sending them is the owner's action.
- US-039 (v0.1.0 release): code complete; the release pull request, PyPI trusted publishing and the tag need the owner.

### Retro

- What slowed us: the first Notion seed used the brief's four use cases and had to be renumbered; a recreated select cleared 32 version fields.
- What went well: the THREATS.md contract test and the fixture pair rule caught two wrong fixtures (a grey-on-grey negative, a missing ToUnicode reference) before they became false claims.
- What to change: pull the View B work earlier in a week (stage 1 confirmation is what makes the detectors honest), which happened here by accident and should be the plan.
- Risk into week 2: v0.2.0 is the HTML report and its design; that work waits for the owner and a design pass.

## Planning (21 to 22 Sep 2026)

- Brief exported to `docs/00-brief/PROJECT_BRIEF.md` and corrected to v0.2 after a verified landscape pass.
- `CLAUDE.md` rewritten from the PermitFlow workflow and the brief: Notion board, `main` sacred, story branches from `dev`, one release per use case, the product contract.
- Notion board "Paperglass" with 7 epics and 90 stories (US-000 to US-099); `docs/05-planning/ISSUES.md` mirrors it.
- Railway project `paperglass` with `development` and `production` environments (nothing deployed until v0.4.0).
- Decisions recorded in `SCOPE.md`: five use cases, cascade View B, possible and confirmed findings, no score, subtractive `clean()`, fingerprint, profiles, MCP receipt gate, docs scan, false-positive bounty, glyph arbiter, disclosure ids; deferred items named.
- Docs tree scaffolded (`docs/README.md` lists status per document).

Handover (22 Sep 2026, end of session): everything through US-038 is merged on `dev` and pushed. Next: the owner configures PyPI trusted publishing for `paperglass` (pending publisher: repository SuhaasNv/paperglass, workflow release.yml, environment pypi), reviews the `dev` to `main` pull request, tags v0.1.0; then v0.2.0 starts with the HTML report design (US-037, US-043, US-044), which the owner wants to design with Fable before code.
