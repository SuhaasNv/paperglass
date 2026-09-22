# REST service (v0.4.0, US-066, US-067)

Planned. `paperglass-server` (fastapi): `POST /v1/scan`, `POST /v1/clean`, `GET /healthz`, `GET /metrics` behind `PAPERGLASS_METRICS_TOKEN`. Same JSON contract as the library; error body `{ "error": { "code", "message", "details"? } }` everywhere; request id on every log line; no document content in logs; request size capped; no persistence by default.

Image: `ghcr.io/suhaasnv/paperglass:<tag>`, non-root, read-only filesystem, recommended run `docker run --network none --read-only --tmpfs /tmp ghcr.io/suhaasnv/paperglass:v0.4.0`. This is the recommended deployment for untrusted volume because a subprocess sandbox does not stop a memory-safety exploit in a native parser from reading the host.

Railway: `development` from `dev` (automatic after green CI), `production` from `main` (approval gate, pinned image, health gate). No latency commitment until after v1.0.0; p95 is measured and printed when it is.
