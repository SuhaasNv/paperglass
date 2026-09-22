# GitHub Action and pre-commit hook (v0.4.0, US-063, US-079)

Planned. `action.yml` runs `paperglass scan <path> --tier fast|standard` and fails the job on `malicious` (configurable to `suspicious`); uploads SARIF when produced. Two modes: documents (a folder of PDFs or DOCX, standard tier) and repository docs (`paperglass scan ./` over Markdown, HTML, README, SKILL.md, CLAUDE.md, MCP tool descriptions: invisible Unicode, hidden DOM, comments; fast tier, no OCR). `.pre-commit-hooks.yaml` exposes the repository-docs mode. This repository runs both on itself.
