# 08-benchmark

The benchmark: corpus, hygiene, harness, baselines, results, Red Kit. Written 22 Sep 2026 as design; numbers appear only in `../../BENCHMARK.md` and only with a command. Benchmark versions are immutable and carry a Zenodo DOI.

| Document | What it holds |
|----------|---------------|
| `BENCHMARK_DESIGN.md` | Sources, licences, splits, leakage and shortcut audits, metrics, what is reported per family |
| `CORPUS_INDEX.md` | The index schema and every source with hash, licence and technique labels (filled at US-050) |
| `HARNESS.md` | The two-function adapter, metrics, commands, results file schema |
| `BASELINES.md` | PhantomLint, OpenDataLoader, DocFirewall, Prompt Guard 2: how each is run, with flags |
| `LEADERBOARD.md` | The `results/` directory, submission rules, versioning; the Space is deferred |
| `REDKIT.md` | The generator: seeds, techniques, matched controls, adding a technique |

Start with `BENCHMARK_DESIGN.md`. Related: `../../THREATS.md`, `../09-testing/FIXTURES.md`.
