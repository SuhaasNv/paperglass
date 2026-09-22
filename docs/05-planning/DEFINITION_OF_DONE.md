# Definition of Done

A story is Done only when every applicable item is true. "Works on my machine" is the start, not the end. Nothing is Done "mostly".

## Story level

Functional
- [ ] Every acceptance criterion of the story is demonstrated by a test or a command named in the pull request.
- [ ] The primary path (install, `paperglass scan` on the demo documents, expected verdict) still passes.

Correctness and safety
- [ ] Every parser call inside the sandbox; a crash is a `parse.failure` finding, never an exception.
- [ ] No execution of document content; no network in tests; no document content in logs.
- [ ] Any change to a technique id, threshold, severity class, schema field, adapter key, CLI exit code or report layout carries a version bump, an ADR and regenerated golden files.

Technique stories
- [ ] Detector registered with `@technique`, emitting `Finding` or `Candidate` only, with `mechanism` and `reproduce` filled.
- [ ] `tests/fixtures/<format>/<technique>/positive.*` and `negative.*`; the positive yields exactly one finding of the technique with confidence above 0.9; the negative yields none.
- [ ] `THREATS.md` row with the plain-language sentence and the threshold; registry test green.
- [ ] Benign-hidden constraint considered and, if relevant, a benign fixture.
- [ ] Benchmark re-run on the affected corpus; false-positive rate on the benign corpus in the pull request (from v0.3.0; before that, on the benign fixtures).

Tests and quality
- [ ] `ruff check`, `ruff format --check`, `mypy --strict`, `pytest` with detector coverage at or above 90 percent, layering test, golden files: green locally and in CI on Linux, macOS and Windows (OCR jobs Linux and macOS until v1.0.0).
- [ ] No `print()` or debug logging in library code; no commented-out code; no `Any` in public signatures; no `# type: ignore` without a code and a reason.
- [ ] AI-generated code read in full and compared with the story before merge.

Dependencies and security
- [ ] Any new dependency: licence MIT, BSD, Apache-2.0 or MPL-2.0; `THIRD_PARTY.md` entry; justification in the commit body.
- [ ] No secrets; `.env.example`, `README.md` and `docs/10-operations/OPERATIONS.md` updated for any new variable.

Documentation
- [ ] The documents the change touches updated in the same change (ARCHITECTURE, VIEWS, FINDING_SCHEMA, TECHNIQUE_REGISTRY, SANDBOX, the adapter page, ADR, `SCOPE.md`, `AI_USAGE.md`, `docs/07-ai/`).
- [ ] No document describes something the code does not do.

Board and history
- [ ] Story branch from `dev`, merged with `--no-ff`; GitHub issue closed by the merge; Notion Status Done; `ISSUES.md` regenerated; `CHANGELOG.md` entry if it is a milestone.

## Release level (weeks 4, 5, 6, 8, 10, 12)

- [ ] Every story in the release's epic Done, or slipped with a note in `SCOPE.md` and `CHANGELOG.md`.
- [ ] `docs/10-operations/RELEASE_CHECKLIST.md` run in full and recorded.
- [ ] `BENCHMARK.md` numbers current for the release (from v0.3.0).
- [ ] `CHANGELOG.md` `## vX.Y.0 (date)` section in users' words before the tag; version bumped in `pyproject.toml`.
- [ ] Pull request `dev` to `main` green on every check; merge commit; annotated tag; GitHub release; PyPI publish; GHCR image (from v0.4.0); Railway production deploy behind approval and health gate (from v0.4.0).
- [ ] `README.md` "What I would do next" names the gaps this release leaves.

## Weekly close

`ROADMAP.md`, "Weekly close ritual".
