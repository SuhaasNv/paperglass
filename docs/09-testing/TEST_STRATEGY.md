# Test strategy

| Layer | What it protects | Where | Run |
|-------|------------------|-------|-----|
| Unit | ingest, sandbox limits, each view, each detector, engine rules (promotion, severity, verdict, allowlist constraints), clean(), schema | `tests/unit/` | `uv run pytest tests/unit` |
| Registry | every `@technique` id has a fixture pair and a `THREATS.md` row with the same sentence and threshold | `tests/unit/test_registry.py` | part of unit |
| Layering | the import rules in `ARCHITECTURE.md` | `tests/unit/test_layering.py` | part of unit |
| Fixtures | positive yields exactly one finding of the technique with confidence above 0.9; negative yields none; benign fixtures yield benign-hidden; false-positive fixtures yield clean | `tests/fixtures/`, `tests/test_fixtures.py` | part of unit |
| Golden | byte-identical JSON report (and HTML from v0.2.0) per fixture; determinism across two runs and across operating systems | `tests/golden/` | part of unit |
| Fuzz | malformed inputs never crash or hang; every failure is a `parse.failure` | `tests/fuzz/` | `uv run pytest tests/fuzz` |
| Adapters | CLI exit codes and output; LangChain, LlamaIndex, Docling, MCP, REST, Action against pinned versions | `tests/adapters/` | extras installed in their own CI job |
| Benchmark | the harness's own logic; a 500-document CI subset of the benign corpus for the false-positive gate | `tests/bench/` | nightly and at release |
| Performance | fast and standard tier latency on the CI runner (informational) and on a named 4-core CPU (published) | `bench/perf/` | at release |

Gates: `ruff check`, `ruff format --check`, `mypy --strict`, `pytest --cov=paperglass --cov-fail-under=90` (detectors and engine counted; adapters have their own gate), layering, golden, fuzz corpus; all on Linux, macOS and Windows (OCR jobs Linux and macOS until v1.0.0).

Principles: test against real files, not mocked parsers; exhaustive enumeration over sampling for table-driven rules (every technique times every profile); one end-to-end test protects the one promise (scan the demo documents, get the expected verdict) and is not a place for edge cases; a covered line is a line that ran, so the percentage is a floor, not the goal; counts of tests and fixtures are stated exactly in `README.md` and recounted before every release.
