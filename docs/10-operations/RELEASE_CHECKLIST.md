# Release checklist

Run before the pull request `dev` to `main`. Everything must be true; record the run in `CHANGELOG.md` under the version.

- [ ] Every story in the release's epic is Done on the board and in `ISSUES.md`, or slipped with a note in `SCOPE.md` and `CHANGELOG.md`.
- [ ] Local gate green: ruff, ruff format, mypy strict, pytest with coverage, layering, golden, fuzz. CI green on `dev` on the three operating systems.
- [ ] `pip install` of the built wheel runs the README steps on Linux, macOS and Windows (the Install job).
- [ ] `THREATS.md` matches the registered detectors; every shipped technique has its fixture pair; the registry test is green.
- [ ] `BENCHMARK.md` numbers current for this release, each with its command (from v0.3.0); synthetic labelled synthetic; non-default flags stated.
- [ ] `SCOPE.md` says what is built, deferred and mocked, with a dated check paragraph for this week.
- [ ] `README.md` describes what exists (install, CLI, adapters, benchmark summary, "What I would do next"); `docs/README.md` status column truthful; `THIRD_PARTY.md` complete; `AI_USAGE.md` current.
- [ ] `SECURITY.md` and the disclosure channel exist; no secrets; gitleaks and pip-audit green.
- [ ] `python scripts/check_copy.py` green (no em dashes, no emoji, no coursework wording).
- [ ] The name, licence and third-party notices are correct.
- [ ] Version bumped in `pyproject.toml`; `CHANGELOG.md` `## vX.Y.0 (date)` section written in users' words.
- [ ] The owner has said yes, in this turn, to the pull request, the tag, the publish and (from v0.4.0) the deploy.

After the merge: annotated tag on the merge commit; GitHub release with the CHANGELOG section; PyPI publish from the tag; GHCR image from the tag; Railway production deploy behind approval with a green health gate; Hugging Face dataset card updated; `main` merged back into `dev`.
