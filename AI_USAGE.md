# AI usage

Paperglass is built with AI assistants (Claude Code, Opus 5) under the standing instructions in `CLAUDE.md`. This page says what the tools do, how their output is checked, and where they were wrong. It is kept short and current; it is not a prompt log.

## What the assistant does

Drafts documents, stories, code and tests against the brief and the rules in `CLAUDE.md`; keeps the Notion board and `docs/05-planning/ISSUES.md` in step; runs the local gate before every commit. Read-only subagents were used on 22 Sep 2026 for three reports: the workflow rules to adopt, the rules implied by the brief, and a critical evaluation of the idea with a verified landscape check.

## What the owner does

Wrote the brief, chose the use cases and the release order, makes every scope decision recorded in `SCOPE.md`, reads the diffs, and gives the yes before any push, tag, publish or deploy.

## How output is checked

Code passes ruff, mypy strict, pytest with coverage, the layering test and golden files before a commit; every generated detector ships with a fixture pair and its false-positive rate in the pull request; benchmark numbers exist only with a reproducing command; subagent findings are claims until verified in the code or the source.

## Where the AI was wrong

- 22 Sep 2026: the first board seed followed the brief's four use cases; it was renumbered after the owner chose five. Recreating a Notion select cleared the version on 32 stories; they were reset by hand.
- The brief's landscape table had four factual errors (OpenDataLoader stars, licence and defaults; PhantomText licence; Lakera price; ASCII-smuggling count) that the verification pass found; the brief is now v0.2.

This section grows as things go wrong. Entries are short.
