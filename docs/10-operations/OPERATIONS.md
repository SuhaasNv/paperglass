# Operations

Describes what exists. Sections are filled as the stories that create them land; until then they say "planned".

## Local setup

`uv sync --all-extras --dev` creates one environment for the library and the backend (a uv workspace); `uv run paperglass --help`. Python 3.11+. No system packages for the fast tier; `paperglass[ocr]` pulls RapidOCR and onnxruntime wheels. Backend (US-046): `docker compose up postgres` (compose file lands with US-048) or any PostgreSQL 16, then in `backend/`: `uv run alembic upgrade head` and `uv run paperglass-backend`, or `uv run uvicorn app.main:app --reload`; with `PAPERGLASS_DATABASE_URL` unset the backend uses a local SQLite file and creates the table itself, which is for local play and tests only. API docs at `/api/docs`. Frontend (US-047): in `frontend/`, `npm install` then `npm run dev` on http://localhost:5173 with `/api` proxied to the backend; `npm test` for the unit tests and `npm run test:e2e` for the Playwright journey, which starts both servers itself.

## Environment variables

None are required to scan a file. `.env.example` documents every variable; each is also listed here when it lands.

| Variable | Default | Used by | Note |
|----------|---------|---------|------|
| `PAPERGLASS_ALLOW_NETWORK` | false | adapters | opt-in network features, named in the report |
| `PAPERGLASS_SANDBOX_SECONDS` | 5 | ingest | wall clock and CPU per parser call |
| `PAPERGLASS_SANDBOX_MEMORY_MB` | 512 | ingest | |
| `PAPERGLASS_MAX_FILE_MB` | 50 | ingest | |
| `PAPERGLASS_MAX_PAGES` | 500 | ingest | |
| `APP_ENV` | development | backend | anything else refuses the placeholder session secret |
| `PAPERGLASS_DATABASE_URL` | sqlite file | backend | PostgreSQL in every deployed environment |
| `PAPERGLASS_SESSION_SECRET` | placeholder | backend | signs the anonymous session cookie; at least 32 characters outside development |
| `PAPERGLASS_CORS_ORIGINS` | localhost | backend | the frontend origins, comma separated |
| `PAPERGLASS_RETENTION_DAYS` | 7 | backend | reports older than this are invisible and purged at startup |
| `PAPERGLASS_MAX_UPLOAD_MB` | 25 | backend | 413 above it |
| `PAPERGLASS_METRICS_TOKEN` | none | backend (v0.4.0) | metrics endpoint off without it |
| `PAPERGLASS_LOG_LEVEL` | info | backend | |

## CI (built at US-004, 22 Sep 2026; `.github/workflows/ci.yml`)

Runs on push to `main` and `dev`, tags `v*`, and pull requests to either. `permissions: contents: read`, `shell: bash` (pipefail), one concurrent run per ref. Jobs: **Lint and types** (ruff check, ruff format, mypy strict, `scripts/check_copy.py`); **Tests** on Linux, macOS and Windows for Python 3.11 and 3.12 (pytest with the coverage gate at 90 percent over the package, switching to detectors and engine at US-008; layering; golden; fuzz corpus from US-021); **Backend on PostgreSQL** (a Postgres 16 service, Alembic up, down and up again, the backend tests in `tests/backend/`); **Install** (build the wheel, install it into a fresh environment on the three systems, run `paperglass version`); **Secret scan** (gitleaks over the full history, fixtures allowlisted in `.gitleaks.toml`); **Dependency audit** (pip-audit strict on the exported runtime requirements; pip-licenses blocks AGPL and GPL and prints the full table to the summary). Planned additions: Docs scan (v0.4.0), Adapters (one job per extra, v0.4.0), Image (v0.4.0, GHCR, `sha-<commit>` and branch tags, `vX.Y.Z` only on a tag). Required checks on `main` are the five job names above once the first run has produced them.

## Release (`.github/workflows/release.yml`, US-039)

`BRANCHING.md` rule 5. On a `v*` tag: the tag must equal `pyproject.toml`'s version; `uv build`; publish to PyPI through trusted publishing from the GitHub environment `pypi` (no token in the repository; the owner registers the pending publisher on PyPI once: project `paperglass`, owner `SuhaasNv`, repository `paperglass`, workflow `release.yml`, environment `pypi`); a GitHub release whose body is the `## vX.Y.Z` section of `CHANGELOG.md`, with the wheel and sdist attached.

## Railway (project created 22 Sep 2026; wiring at US-048, v0.2.0)

One project, `paperglass`, two environments that share nothing, each with its own Postgres and the `backend` and `frontend` services from GHCR images: `development` deploys from `dev` automatically after a green CI; `production` deploys from `main` only, by hand, behind a GitHub environment approval, pinned to a `sha-<commit>` image, with a health gate on `/healthz` and the frontend's runtime config. Secrets are set by the owner from the Railway CLI or dashboard, never through the assistant. Rollback is the previous pin and the same deploy job. Cost stays within the free allowance; anything beyond is asked for first.

## Observability (planned, US-089)

The REST service exposes `/metrics` behind a token; Prometheus and Grafana run under a compose profile locally and as two Railway services; the dashboard and alert rules are generated by scripts under `scripts/observability/`. Full description: `../15-observability/OBSERVABILITY.md`.

## Hugging Face (planned, US-055)

Dataset card for the corpus index (CC BY 4.0), updated at each benchmark version with its DOI.

## Retention and personal data (US-025, 22 Sep 2026)

`--redact` (or `redact=True`) shortens extracted text to 80 characters and drops every crop, so a stored report carries the least content that still names the finding. There is no telemetry: the library, the CLI and the future service never call home. The library keeps nothing. The REST service keeps no documents and no reports by default; the receipt cache (hash, verdict, versions) is in memory and cleared on restart. Guidance for operators who add persistence: store reports with `--redact`, set a retention period, never log content.

## Rollback

Code: the previous pin and the deploy job. A release that fails after publish: a `hotfix/*` branch, a patch tag; PyPI releases are never deleted, a yanked release is marked yanked with a reason.
