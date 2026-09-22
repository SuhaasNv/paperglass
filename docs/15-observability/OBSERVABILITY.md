# Observability (v0.4.0, US-089)

The library and the CLI emit nothing. The REST service exposes Prometheus metrics; Prometheus and Grafana run beside it, locally under a compose profile and on Railway as their own services. The dashboard and the alert rules are generated from scripts and never edited by hand.

## Metrics endpoint

`GET /metrics`, Prometheus text format, behind `PAPERGLASS_METRICS_TOKEN` (404 without a token configured, 401 without the header). Exempt from request limits; its own scrapes are not counted. No document content, no hashes of documents, no client identifiers in labels.

| Family | Type | Labels | Meaning |
|--------|------|--------|---------|
| `paperglass_scans_total` | counter | verdict, tier, profile, format | scans completed |
| `paperglass_findings_total` | counter | technique_id, status, severity | findings emitted |
| `paperglass_stage_seconds` | histogram | stage (0 to 4) | latency per cascade stage per page |
| `paperglass_scan_seconds` | histogram | tier | end-to-end latency per document |
| `paperglass_parse_failures_total` | counter | parser, reason | `parse.failure` findings |
| `paperglass_sandbox_kills_total` | counter | limit (cpu, memory, wall, size, pages) | limit hits |
| `paperglass_request_bytes` | histogram | endpoint | request sizes |
| `paperglass_http_requests_total` | counter | route, status | with a request-duration histogram |
| `paperglass_receipts_cached` | gauge | | MCP and REST receipt cache size |
| `paperglass_build_info` | gauge | version, rule_versions_hash | 1 |

## Dashboard (Grafana, generated)

`scripts/observability/build_dashboard.py` writes `docker/observability/grafana/dashboards/paperglass.json`: header (version, environment selector), a stat strip (scans per hour, verdict mix, p50 and p95 per tier), a row per cascade stage, parse failures and sandbox kills, findings by technique, HTTP health. One dashboard, two environments (development, production) selected by a variable.

## Alert rules (generated)

`scripts/observability/build_alerting.py` writes the Prometheus rules: HTTP error rate above 5 percent for 10 minutes; p95 scan latency above the tier budget times 3 for 15 minutes; `parse.failure` rate above 10 percent of scans; any sandbox kill on memory; scrape target down for 5 minutes; disk on the Prometheus volume above 80 percent. Notification target is decided at the story (a Telegram bot as in the owner's earlier project, or GitHub issues); the rules file is the same either way.

## Local

`docker compose --profile observability up` starts the service, Prometheus (rendered config) and Grafana with the provisioned dashboard at `localhost:3000`.

## Railway

Two services in the `paperglass` project, `prometheus` (private, a volume) and `grafana` (a volume, a public host), from public images with their configuration in variables so the "Railway never builds" rule holds. Prometheus scrapes both environments over HTTPS with one token each. Secrets are set by the owner from the CLI, never through the assistant.

## What it does not do

No tracing, no log shipping, no per-document records. Logs carry request ids, never content.
