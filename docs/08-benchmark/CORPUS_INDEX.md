# Corpus index

Filled at US-050 (week 5). Schema of one index row (`datasets` feature set):

| Field | Meaning |
|-------|---------|
| `sample_id` | stable id, `<source>-<n>` |
| `sha256` | hash of the file; the file itself lives in the source's own distribution or is generated |
| `source` | crackedpdfs, phantomtext, semantic_integrity, phantomlint, redkit, benign_<name> |
| `source_version` | the upstream version or the generator version and seed |
| `licence` | per source |
| `format` | pdf, docx, html, md, pptx, png |
| `labels` | list of technique ids (empty for benign) |
| `family` | attack family for held-out reporting (visual, structural, semantic-override, unicode, metadata) |
| `injection_kind` | instruction, data, none |
| `base_document` | id of the clean base for the provenance split |
| `split` | train, test, unseen_generator |
| `caveat` | free text, for example the CrackedPDFs erratum |

The index is published as a Hugging Face dataset card (CC BY 4.0) with the hashes; files that may not be redistributed are fetched by `paperglass bench fetch` from their source.
