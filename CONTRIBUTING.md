# Contributing

Thank you. Paperglass is one maintainer plus whoever shows up; the two recipes below are the fastest way to help.

## Ground rules

- Sign your commits with the Developer Certificate of Origin (`git commit -s`); by signing you certify https://developercertificate.org/.
- Conventional commit messages (`feat:`, `fix:`, `test:`, `bench:`, `docs:`, `chore:`), subject at most 50 characters.
- No em dashes, no emoji in documents or copy (`scripts/check_copy.py` runs in CI).
- Branch from `dev`; `main` only receives releases (`docs/10-operations/BRANCHING.md`).
- Security issues go through `SECURITY.md`, never a public issue.
- Issue templates: new technique, false positive, new sample. A false-positive report is answered before feature work.

## Add a technique

1. Open an issue with the "new technique" template: what is hidden, how, which format, a sample if you may share one.
2. Branch from `dev`: `feat/uc<N>-us<xxx>-<slug>` (the maintainer assigns the story id).
3. Write the detector under `src/paperglass/detectors/<format>/<slug>.py`, registered with `@technique("<format>.<object>.<what>")`, emitting `Finding` objects only, with `mechanism` and `reproduce` filled.
4. Add `tests/fixtures/<format>/<technique>/positive.<ext>` and `negative.<ext>`; the positive yields exactly one finding of the technique with confidence above 0.9, the negative yields none.
5. Add the `THREATS.md` row with the plain-language sentence and the threshold; the registry test fails until the row and the code agree.
6. Run the benchmark on the affected corpus and put the false-positive rate on the benign corpus in the pull request.
7. Update `docs/03-architecture/TECHNIQUE_REGISTRY.md` if you added a new mechanism type.

## Add a sample

1. Use the "new sample" issue template: technique, format, source, licence, whether it is real or generated (Red Kit seed if generated).
2. Put it under `tests/fixtures/<format>/<technique>/` (positive or negative) or, for a false positive you hit on a real document, under `tests/fixtures/false-positives/<issue>/`.
3. Never a real resume or any document with personal data.
4. A false-positive sample becomes a permanent negative fixture with your name in `CONTRIBUTORS.md` (v0.3.0, US-057).

## Local gate before a pull request

`uv run ruff check . && uv run ruff format --check . && uv run mypy --strict && uv run pytest` (coverage on detectors at or above 90 percent). CI runs the same on Linux, macOS and Windows.

## Code of conduct

`CODE_OF_CONDUCT.md`. Contributors are listed in `CONTRIBUTORS.md`.
