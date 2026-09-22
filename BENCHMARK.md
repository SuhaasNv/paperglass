# BENCHMARK.md

No numbers yet. This file gains a number only when the number reproduces from a clean clone with one command, names the corpus and the benchmark version, states any non-default flag, and labels synthetic data as synthetic. Benchmark versions are immutable and carry a Zenodo DOI. Design: `docs/08-benchmark/BENCHMARK_DESIGN.md`. Harness: `docs/08-benchmark/HARNESS.md`. Baselines: `docs/08-benchmark/BASELINES.md`. Results directory accepting pull requests: `results/` (v0.3.0).

## Targets that gate v1.0.0 (brief section 11, amended 22 Sep 2026)

| Area | Target | How measured |
|------|--------|--------------|
| Detection | recall at or above 0.90 on every PhantomText technique; 25 of 25 Semantic Integrity canaries flagged; CrackedPDFs held-out F1 at or above 0.95 as a sanity check (its payloads are nearly all off-page) | `paperglass bench --corpus <name> --version v1` |
| Data versus instruction | data-injection recall reported separately from instruction-injection recall | per-family table |
| False positives | verdict-driving findings at or below 0.1 percent on at least 5,000 benign real documents; zero benign-hidden items labelled malicious; informational findings reported with no target | benign corpus run |
| Fidelity | `clean()` retains at least 99.9 percent of benign words on the benign corpus | fidelity column |
| Speed | fast tier at or below 100 ms per page; standard p50 at or below 300 ms, p95 at or below 1 s on a 4-core CPU | latency column, hardware named |
| Hygiene | hard-provenance split, unseen-generator split, label-shuffle check collapses to 0.5, shortcut audit (text-only TF-IDF must not score well) | `docs/08-benchmark/BENCHMARK_DESIGN.md` |

## Honesty rules

If a baseline was run with a non-default flag, it says so here. If a number comes from synthetic data only, the table says synthetic. PhantomLint is phrase-gated and its published 0.092 percent false-positive rate was measured after that gate; it is reported with and without the gate where its code allows, and on data-injection samples where its recall is unmeasured. CrackedPDFs v1 placement labels record requested, not actual, positions. Paperglass numbers are published only on corpora Paperglass did not generate; Red Kit samples are labelled as ours.
