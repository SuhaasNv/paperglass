# Harness

Built at US-052 (22 Sep 2026): `src/paperglass/bench/` (adapter, index, metrics, run, report), `paperglass bench fetch|run|report|verify`, `results/` with Paperglass's own file for the `fixtures` corpus, and a CI step that re-runs it. Metrics are plain Python; scikit-learn stays in the `bench` extra for the shortcut audit (US-053). Two recalls are reported: verdict recall (the share of positives called suspicious or malicious; structure-only techniques never drive a verdict by contract, so it is a sanity number) and detection recall (every label named by a finding of any status), plus recall per technique and per family, instruction versus data recall, the two false-positive rates, benign-hidden mislabelled as malicious, and latency p50 and p95.

## Two-function adapter

Any detector implements:

```python
def scan(path: str) -> dict:      # {"verdict": str, "findings": [{"technique_id": str, "page": int|None, "bbox": [..]|None, "severity": str, "confidence": float}]}
def version() -> str
```

Paperglass's own adapter maps its `Report` to that shape. Baselines wrap their CLI or API (`BASELINES.md`).

## Commands

`paperglass bench fetch --corpus v1` downloads or generates every sample the index names and verifies hashes (`--force` rebuilds a generated index, dropping its split).
`paperglass bench run --corpus v1 --detector paperglass` (or `--detector module:scan`) writes `results/<detector>/<version>/<corpus>.json`.
`paperglass bench report --corpus v1` renders the tables in `BENCHMARK.md` from `results/`.
`paperglass bench split --corpus v1 [--test-share 0.3] [--seed 1] [--held-out-source redkit]` writes a hard-provenance split into the index: whole base documents per side, a held-out source in full as `unseen_generator`; refuses a split where a base document straddles (US-053).
`paperglass bench audit --corpus v1 --results results/<detector>/<version>/v1.json` runs the label-shuffle check on that results file (F1 with permuted labels must fall to chance plus a margin) and the text-only shortcut audit (a TF-IDF logistic regression on View A text, fit on train, scored on test; above 0.8 accuracy the split is a shortcut); scikit-learn comes with `pip install 'paperglass[bench]'`, without it the audit says so (US-053). Results files carry `metrics_per_split` when the index has a split.
`paperglass bench verify --corpus v1 --results results/<detector>/<version>/<corpus>.json` re-runs a committed file's command and refuses it if the numbers differ (latency excluded).

## Results file

`{ "detector", "detector_version", "corpus_version", "command", "hardware", "date", "metrics": { ... per BENCHMARK_DESIGN }, "per_sample": [...] }`. The `command` must reproduce the file from a clean clone; CI re-runs a sample of it.
