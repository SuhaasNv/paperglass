# Documentation index

Each numbered folder has its own `README.md` (what it is for, one line per document, where to start). Status: **written** (planning, 22 Sep 2026, before code; describes the intended design and is amended in place as built) or **to be written** (produced during or after the story named).

| Folder | Documents | Status |
|--------|-----------|--------|
| `00-brief/` | `PROJECT_BRIEF.md` (v0.2), `LANDSCAPE.md` (verified 22 Sep 2026) | written |
| `01-discovery/` | `PROBLEM.md`, `PERSONAS.md` | written |
| `02-requirements/` | `REQUIREMENTS.md` (FR, NFR, SEC, BENCH, REP), `USE_CASES.md` (UC1 to UC5) | written |
| `03-architecture/` | `ARCHITECTURE.md`, `VIEWS.md`, `FINDING_SCHEMA.md`, `TECHNIQUE_REGISTRY.md`, `SANDBOX.md`, `decisions/` (ADR-001 to ADR-006), `diagrams/` | written and amended as built through US-038 (22 Sep 2026); diagrams to be written (US-081) |
| `04-report-design/` | `REPORT_DESIGN.md`, `CLI_DESIGN.md`, `ACCESSIBILITY.md` | CLI as built; report design written, to be revised with the owner before v0.2.0 |
| `05-planning/` | `ROADMAP.md`, `ISSUES.md` (90 stories, mirrored from the board), `DEFINITION_OF_DONE.md`, `RELEASE_PLAN_V0_1_0.md` | written |
| `06-security/` | `THREAT_MODEL.md` (T1 to T16), `FUZZING.md` | written; `SECURITY_REVIEW.md` to be written (US-080) |
| `07-ai/` | `CLASSIFIER_DESIGN.md`, `PROMPTS.md` | written; `AI_EVALUATION.md` only if the deep tier is built |
| `08-benchmark/` | `BENCHMARK_DESIGN.md`, `HARNESS.md`, `BASELINES.md`, `LEADERBOARD.md`, `REDKIT.md` | written as design; `CORPUS_INDEX.md` filled at US-050 |
| `09-testing/` | `TEST_STRATEGY.md`, `FIXTURES.md` | written and amended as built |
| `10-operations/` | `BRANCHING.md`, `OPERATIONS.md`, `RELEASE_CHECKLIST.md` | written; CI and retention sections as built; release workflow `release.yml` |
| `11-integrations/` | one page per adapter | planned pages; rewritten as built (v0.4.0) |
| `12-reviews/` | `FALSE_POSITIVE_REVIEW.md` | log, empty |
| `13-demo/` | `DEMO_SCRIPT.md`, `documents/` | script written; documents at US-019 |
| `14-community/` | `LAUNCH_PLAN.md`, `GOOD_FIRST_ISSUES.md`, `ADVISORS.md` | written |
| `15-observability/` | `OBSERVABILITY.md` | planned (US-089, v0.4.0); rewritten as built |

Root: `README.md`, `SCOPE.md`, `THREATS.md`, `BENCHMARK.md` (no numbers yet), `AI_USAGE.md`, `CHANGELOG.md`, `SECURITY.md`, `THIRD_PARTY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `CLAUDE.md`, `LICENSE`.
