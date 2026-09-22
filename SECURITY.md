# Security policy

Paperglass parses untrusted files. Vulnerabilities in the scanner itself (a crafted file that escapes the sandbox, hangs a parser, exhausts memory, reads outside its inputs, or makes a network call) and detection bypasses that the threat matrix claims to cover are both security issues.

## Reporting

Email the maintainer at the address on the GitHub profile with "Paperglass security" in the subject, or use GitHub's private vulnerability reporting on this repository. Do not open a public issue. You will get an acknowledgement within 7 days and a fix or a written plan within 90 days; after 90 days you may disclose. Credit is given in the release notes unless you ask otherwise.

## New hiding techniques

A technique Paperglass does not detect is reported the same way. It gets a stable technique id, a fixture pair and a `THREATS.md` row; the fixture stays private for 30 days after the detector ships, then becomes public (v0.5.0, US-088).

## Scope

In scope: the `paperglass` package, the CLI, the REST service image, the MCP server, the GitHub Action, the benchmark harness. Out of scope: vulnerabilities in third-party parsers that Paperglass already mitigates through the sandbox (report those upstream; tell us too so we can pin a fixed version).

## Supported versions

The latest minor release. Security fixes are released as patch versions from `main` via `hotfix/*` branches (`docs/10-operations/BRANCHING.md`).

## What the scanner promises

No document content is executed. No network call without `allow_network`. No document content in logs by default. Every parser call bounded by CPU, memory and time. Details: `docs/06-security/THREAT_MODEL.md`.
