# Corpus indexes

`<name>/index.jsonl`: the first line names the corpus (`name`, `version`, `synthetic`, `samples`), every other line is one sample in the shape of `docs/08-benchmark/CORPUS_INDEX.md`. Files are not stored here: `paperglass bench fetch --corpus <name>` builds or downloads them and verifies every hash against the index. `fixtures` is built from `tests/fixtures/` and committed so a clean clone reproduces the results in `results/`.
