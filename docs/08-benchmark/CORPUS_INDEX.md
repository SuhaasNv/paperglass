# Corpus index

Built at US-050 (22 Sep 2026): `src/paperglass/bench/index.py` (the row model, JSON lines, the head line carries the corpus root relative to the repository) and `src/paperglass/adapters/corpus/` (one module per external source). `paperglass bench fetch --corpus v1 [--source name] [--limit N] [--seed S]` fetches or generates the files under `bench/corpus/v1/files/` (never committed), writes `bench/corpus/v1/index.jsonl` (committed) and verifies every hash. It is the one command in the benchmark that touches the network, and only when run by hand.

| Source | How | Pinned | Labels | Notes |
|--------|-----|--------|--------|-------|
| `crackedpdfs` | Hugging Face dataset `volkthienpreecha/crackedpdfs`, `data/labels.parquet` and `data/splits.json`, the PDFs extracted from the two archives (590 MB, cached under `bench/corpus/v1/cache/`) | revision `245bc98e` (the paper release) | `rendering_regime` to `pdf.render.mode`, `pdf.text.low_contrast`, `pdf.text.tiny`; an off-page `spatial_regime` adds `pdf.text.offpage`; a plainly visible payload is `visible.instruction` (family `visible`, which Paperglass defers by contract; the row stays so the boundary is measured) | the paper's frozen test split is kept; `--limit` samples whole base documents (original, confounder, injected together); every row carries the 2026-09 erratum |
| `phantomlint` | GitHub `tobycmurray/phantom-lint`, `tests/bad` (hidden prompts) and `tests/good`, PDFs only until HTML lands (v0.4.0) | commit `7f6200145abf` | positives carry the wildcard `*` (hidden text of unspecified technique): detected when the detector names any technique | real arXiv papers and CVs; BSD-3 |
| `phantomtext` | generated with the Padua toolkit from Paperglass's own clean documents when the toolkit is installed; never downloaded, never redistributed | toolkit version recorded at generation | `camouflage` to `pdf.text.low_contrast`, `outofbound` to `pdf.text.offpage`, `transparent` to `pdf.text.opacity`, `zerosize` to `pdf.text.tiny` | the generation itself is wired at US-054 with the baselines; today the source reports why it did not run |
| `semantic_integrity` | rebuilt canaries | v0.5.0 with the glyph arbiter (US-087) | | not in v1 |
| `redkit` | Paperglass Red Kit | v0.5.0 (benchmark v2) | | never a headline number |

Schema of one index row:

| Field | Meaning |
|-------|---------|
| `sample_id` | stable id, `<source>-<n>` |
| `sha256` | hash of the file; the file itself lives in the source's own distribution or is generated |
| `source` | crackedpdfs, phantomtext, semantic_integrity, phantomlint, redkit, benign_<name> |
| `source_version` | the upstream version or the generator version and seed |
| `licence` | per source |
| `format` | pdf, docx, html, md, pptx, png |
| `labels` | list of technique ids (empty for benign); `*` for hidden text of unspecified technique; `visible.instruction` for a plainly visible payload |
| `family` | attack family for held-out reporting (visual, structural, semantic-override, unicode, metadata, visible, none) |
| `injection_kind` | instruction, data, none |
| `base_document` | id of the clean base for the provenance split |
| `split` | train, test, unseen_generator |
| `caveat` | free text, for example the CrackedPDFs erratum |

The index is published as a Hugging Face dataset card (CC BY 4.0) with the hashes; files that may not be redistributed are fetched by `paperglass bench fetch` from their source.
