# Harness

## Two-function adapter

Any detector implements:

```python
def scan(path: str) -> dict:      # {"verdict": str, "findings": [{"technique_id": str, "page": int|None, "bbox": [..]|None, "severity": str, "confidence": float}]}
def version() -> str
```

Paperglass's own adapter maps its `Report` to that shape. Baselines wrap their CLI or API (`BASELINES.md`).

## Commands

`paperglass bench fetch --corpus v1` downloads or generates every sample the index names and verifies hashes.
`paperglass bench run --corpus v1 --detector paperglass` (or `--detector module:scan`) writes `results/<detector>/<version>/<corpus>.json`.
`paperglass bench report --corpus v1` renders the tables in `BENCHMARK.md` from `results/`.
`paperglass bench audit --corpus v1` runs the label-shuffle and shortcut audits.

## Results file

`{ "detector", "detector_version", "corpus_version", "command", "hardware", "date", "metrics": { ... per BENCHMARK_DESIGN }, "per_sample": [...] }`. The `command` must reproduce the file from a clean clone; CI re-runs a sample of it.
