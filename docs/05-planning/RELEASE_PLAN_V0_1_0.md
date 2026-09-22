# Release plan: v0.1.0, UC1 Scan and Verdict (end of week 4, 19 Oct 2026)

Goal: `pip install paperglass` on Linux, macOS and Windows; `paperglass scan` on a PDF or DOCX returns a verdict from confirmed findings with mechanism and reproduce for every MUST technique in `THREATS.md` for those formats; `paperglass fingerprint` shows which extractors are fooled; a JSON report validated against schema v1; fast tier at or below 100 ms per page measured. Quiet release: PyPI, GitHub release, `CHANGELOG.md`; the public demo waits for v0.2.0.

## Order of work

Week 1 (E0): US-000 skeleton and layering test; US-001 schema and golden test; US-002 registry and `THREATS.md` test; US-003 sandbox; US-004 CI matrix and protection; US-005 governance files; US-006 View A; US-022 advisors, name check, ATR scan-target proposal.

Week 2 (UC1): US-007 View C probes first (it blocks every detector); then US-008 low contrast, US-009 tiny, US-010 off-page, US-011 render mode, US-012 opacity, US-013 hidden layer, US-018 Unicode probe, US-024 mechanism and reproduce in every detector, US-019 fixtures import, US-020 verdict rules and allowlist, US-021 fuzz. Slip candidates to week 3: US-014 ToUnicode (static, informational), US-015 ActualText, US-016 metadata, US-017 annotations and active content.

Week 3: US-030 View B cascade (stage 1 ink check, stage 2 crops); US-031 discrepancy engine (promotion, severity classes, verdict); US-032 covered text; US-033 font decoding fallbacks (informational); US-034 DOCX; US-023 fingerprint; the week 2 slips.

Week 4: US-036 CLI (`scan`, `fingerprint`, `show`, exit codes, `--tier`); US-038 instruction hook (modifier only); US-025 redact, no telemetry, retention note; US-039 release: version bump, `CHANGELOG.md` v0.1.0 section, pull request `dev` to `main`, tag, PyPI trusted publishing, GitHub release.

## Exit criteria

- Every `THREATS.md` row marked v0.1.0 has status covered (PDF and DOCX) or partial with the gap named (ToUnicode and ActualText possible-only).
- `tests/fixtures/` holds a pair per shipped technique plus the five benign fixtures; registry test green.
- Golden files for the JSON report on every fixture; determinism test green.
- Fuzz corpus (PDF, DOCX) green in CI on three operating systems.
- Fast tier p50 and p95 per page and standard tier p50 per page measured on a named 4-core CPU and written in `BENCHMARK.md` under "Speed (synthetic fixtures, v0.1.0)".
- `README.md` install and CLI sections describe what exists; `docs/README.md` status column truthful; `SCOPE.md` week 4 check paragraph.
- `RELEASE_CHECKLIST.md` green.

## Cut first if behind (from `ROADMAP.md`)

Fingerprint extractors beyond three; static ToUnicode and ActualText probes ship informational (already the plan); `pdf.text.covered` if stage 2 is late (document as gap); DOCX View B (already structure-only).

## Not in v0.1.0

HTML report (v0.2.0), profiles beyond default, benchmark, adapters, images, PPTX, HTML.
