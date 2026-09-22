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
| `PAPERGLASS_RETENTION_DAYS` | 7 | backend | reports older than this are invisible and deleted by the sweep |
| `PAPERGLASS_PURGE_INTERVAL_MINUTES` | 60 | backend | the retention sweep runs at startup and then on this interval (UC2 review, finding 1) |
| `PAPERGLASS_MAX_UPLOAD_MB` | 25 | backend | 413 above it |
| `PAPERGLASS_METRICS_TOKEN` | none | backend (v0.4.0) | metrics endpoint off without it |
| `PAPERGLASS_LOG_LEVEL` | info | backend | |

## CI (built at US-004, 22 Sep 2026; `.github/workflows/ci.yml`)

Runs on push to `main` and `dev`, tags `v*`, and pull requests to either. `permissions: contents: read`, `shell: bash` (pipefail), one concurrent run per ref. Jobs: **Lint and types** (ruff check, ruff format, mypy strict, `scripts/check_copy.py`); **Tests** on Linux, macOS and Windows for Python 3.11 and 3.12 (pytest with the coverage gate at 90 percent over the package, switching to detectors and engine at US-008; layering; golden; fuzz corpus from US-021); **Backend on PostgreSQL** (a Postgres 16 service, Alembic up, down and up again, the backend tests in `tests/backend/`); **Install** (build the wheel, install it into a fresh environment on the three systems, run `paperglass version`); **Secret scan** (gitleaks over the full history, fixtures allowlisted in `.gitleaks.toml`); **Dependency audit** (pip-audit strict on the exported runtime requirements; pip-licenses blocks AGPL and GPL and prints the full table to the summary). Planned additions: Docs scan (v0.4.0), Adapters (one job per extra, v0.4.0), Image (v0.4.0, GHCR, `sha-<commit>` and branch tags, `vX.Y.Z` only on a tag). Required checks on `main` are the five job names above once the first run has produced them.

## Release (`.github/workflows/release.yml`, US-039)

`BRANCHING.md` rule 5. On a `v*` tag: the tag must equal `pyproject.toml`'s version; `uv build`; publish to PyPI through trusted publishing from the GitHub environment `pypi` (no token in the repository; the owner registers the pending publisher on PyPI once: project `paperglass`, owner `SuhaasNv`, repository `paperglass`, workflow `release.yml`, environment `pypi`); a GitHub release whose body is the `## vX.Y.Z` section of `CHANGELOG.md`, with the wheel and sdist attached.

## Containers (US-048)

`backend/Dockerfile` (build context: the repository root) installs the library with the `ocr` extra and the backend into one non-root image; on start it runs `alembic upgrade head` and serves on `$PORT` (8000 by default) behind `--proxy-headers`. `frontend/Dockerfile` builds the app and serves it from nginx on `$PORT` (8080), proxying `/api/` and `/healthz` to `$BACKEND_URL` on the same origin, with a Content-Security-Policy that allows no foreign origin. `compose.yaml` runs PostgreSQL, the backend and the app on http://localhost:8080 (`docker compose up --build`). The **Images** workflow (`.github/workflows/images.yml`) builds both on every push to `dev`, `main` and a `v*` tag, smoke tests them (health, one scan, the security headers) and pushes `ghcr.io/suhaasnv/paperglass-backend` and `ghcr.io/suhaasnv/paperglass-frontend` tagged with the branch, the version and the commit; pull requests build without pushing.

## Railway (project `paperglass`, services created 22 Sep 2026 at US-048)

One project (`7954aa45-01bb-43e4-bf5e-ca608f1b3127`), two environments that share nothing: `development` (`5329adbe-65f0-478b-bd7a-a78486bd7d08`) and `production` (`143e1a4e-e122-41e9-80e5-9dd4e9478bf7`), region us-west2.

| Service | Source | development | production |
|---------|--------|-------------|------------|
| `Postgres` / `Postgres-0biU` | Railway Postgres template (postgres-ssl 18, 5 GB volume), database `paperglass` | `Postgres` | `Postgres-0biU` |
| `backend` | this repository, `backend/Dockerfile`, watch `/src/**`, `/backend/**`, `/pyproject.toml`, `/uv.lock`; health `/healthz`; private only | branch `dev` | branch `main` |
| `frontend` | this repository, root `/frontend`, its Dockerfile; health `/`; the only public service | branch `dev`, https://frontend-development-341b.up.railway.app | branch `main`, https://frontend-production-ae91.up.railway.app |

Both environments wait for the GitHub check suites before deploying ("wait for CI" on every trigger), so a red CI never reaches a server. `production` changes only when `main` does, which is a release pull request. Variables: backend `APP_ENV` (`staging` in development, `production` in production), `PORT=8000`, `PAPERGLASS_DATABASE_URL=${{Postgres.DATABASE_URL}}` (the backend rewrites the scheme for pg8000), `PAPERGLASS_CORS_ORIGINS=https://${{frontend.RAILWAY_PUBLIC_DOMAIN}}`, retention and upload defaults; frontend `PORT=8080`, `BACKEND_URL=http://${{backend.RAILWAY_PRIVATE_DOMAIN}}:8000`. `PAPERGLASS_SESSION_SECRET` is set by the owner in each environment (`railway variable set PAPERGLASS_SESSION_SECRET=$(openssl rand -hex 32) --service backend --environment <name>`); the backend refuses to start without it outside development. Rollback is Railway's redeploy of the previous deployment. The backend trusts `X-Forwarded-*` from any address (`--forwarded-allow-ips='*'`), which is fine while nothing reads the client address; US-066 (rate limits) must pin it to Railway's edge first (UC2 review, finding 4). Cost stays within the free allowance; anything beyond is asked for first.

## Observability (planned, US-089)

The REST service exposes `/metrics` behind a token; Prometheus and Grafana run under a compose profile locally and as two Railway services; the dashboard and alert rules are generated by scripts under `scripts/observability/`. Full description: `../15-observability/OBSERVABILITY.md`.

## Hugging Face (planned, US-055)

Dataset card for the corpus index (CC BY 4.0), updated at each benchmark version with its DOI.

## Retention and personal data (US-025, 22 Sep 2026)

`--redact` (or `redact=True`) shortens extracted text to 80 characters and drops every crop, so a stored report carries the least content that still names the finding. There is no telemetry: the library, the CLI and the future service never call home. The library keeps nothing. The REST service keeps no documents and no reports by default; the receipt cache (hash, verdict, versions) is in memory and cleared on restart. Guidance for operators who add persistence: store reports with `--redact`, set a retention period, never log content.

## Rollback

Code: the previous pin and the deploy job. A release that fails after publish: a `hotfix/*` branch, a patch tag; PyPI releases are never deleted, a yanked release is marked yanked with a reason.
