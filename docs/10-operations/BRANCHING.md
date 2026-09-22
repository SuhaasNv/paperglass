# Branching

Two long-lived branches, short-lived story branches, merges only through the chain below. `main` is what a visitor sees on GitHub and is never broken.

```
main  production releases only. Default branch on GitHub. Protected. Tagged vX.Y.Z on every release. Never a direct commit.
  dev  integration. Always green. Receives every story branch with --no-ff. Protected against force push and deletion.
        feat/uc1-us008-low-contrast
        bench/uc3-us054-baselines
        docs/uc4-us060-langchain-guide
        chore/e0-us004-ci-matrix
        docs/e0-week-3-close
hotfix/<slug>  from main, for a broken published release; pull request to main, patch tag, then merged into dev.
```

| Branch | From | Merges into | Naming |
|--------|------|-------------|--------|
| `main` | none | none | |
| `dev` | `main` | `main` by pull request at a release | |
| story | `dev` | `dev`, `--no-ff` | `<type>/uc<N>-us<xxx>-<slug>` or `<type>/e<N>-us<xxx>-<slug>`; types `feat`, `fix`, `test`, `bench`, `docs`, `chore` |
| week close | `dev` | `dev`, `--no-ff` | `docs/e0-week-<n>-close` |
| `hotfix/*` | `main` | `main` then `dev` | `hotfix/<slug>` |

## Rules

1. One story per branch; the branch name carries the use case (or epic) and the story id, so the history maps to the board.
2. Merge into `dev` with `git merge --no-ff` and the message `<type>: <what> (US-xxx)`; the remote story branch is kept so the history reads branch by branch; the local branch may be deleted.
3. Commits are conventional; subject at most 50 characters, never over 72, no trailing period; body explains why when not obvious; explicit staging; no AI attribution.
4. `main` is protected: pull request from `dev` with every CI check green, no force push, no deletion, applies to the owner. `dev` is protected against force push and deletion. History is never rewritten on either.
5. A release is: `RELEASE_CHECKLIST.md` green, version bumped in `pyproject.toml`, `CHANGELOG.md` version section, pull request `dev` to `main` merged with a merge commit, annotated tag `vX.Y.0` on that commit, GitHub release, PyPI publish from the tag (trusted publishing), GHCR image from the tag when Docker exists, Railway production deploy behind approval when the REST service exists, then `main` merged back into `dev`. CI refuses a tag that does not match `pyproject.toml`.
6. Nothing is pushed, tagged, published or deployed without the owner's yes in that turn. When the owner is absent the work stops at the story branch: no merge into `dev`, no push.
7. The first commit of the repository lands on `main` so that `main` is the default branch; `dev` is created from it. `dev` never becomes the default.

## Day to day

```
git switch dev && git pull
git switch -c feat/uc1-us008-low-contrast
# work, gate, commit
git switch dev
git merge --no-ff feat/uc1-us008-low-contrast -m "feat: low-contrast text detector (US-008)"
git branch -d feat/uc1-us008-low-contrast
```
