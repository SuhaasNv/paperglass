# ADR-006: Delivery pipeline

Date 22 Sep 2026. Status: accepted, not yet built (US-004, US-039, US-067).

## Context
One maintainer, six releases in twelve weeks, a public package, a Docker service and a benchmark dataset. The owner's PermitFlow project established a branching and release discipline worth keeping.

## Constraints
`main` must be what a visitor sees and must never be broken; a green CI on a weekend must not change production; every story visible as one merge; no push, tag, publish or deploy without the owner's yes.

## Options considered
### Option A: `main` sacred and default, `dev` integration, story branches from `dev` merged `--no-ff`, release by pull request `dev` to `main` and an annotated tag, PyPI trusted publishing from the tag, GHCR images tagged by sha and by release, Railway development (auto from `dev`) and production (from `main`, approval gate, health gate, pinned image)
- Pros: history reads story by story; releases are explicit; rollback is a pin; production needs a person.
- Cons: more ceremony than trunk-based for a solo project.
### Option B: trunk-based on `main`
- Pros: fewer branches.
- Cons: `main` breaks; no natural release moment; every push is production-adjacent.
### Option C: Railway builds from the repository
- Pros: no image registry.
- Cons: the deployed artefact is not the tested artefact.

## Decision
Option A, written down in `../../10-operations/BRANCHING.md` and `OPERATIONS.md`.

## Rationale
The discipline costs minutes per story and buys a history and a production that can be trusted.

## Consequences
### Positive
Six clean release points; a `results/` and a docs site that always match a tag.
### Negative
The first push sets the default branch, so the first commit must land on `main` before `dev` exists.

## Validation
Branch protection visible on GitHub; CI refuses a tag that does not match `pyproject.toml`; the deploy job's health gate.
