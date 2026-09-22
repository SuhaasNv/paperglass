# Finding schema

Schema version 1, designed and built 22 Sep 2026 (US-001) in `src/paperglass/report/schema.py`. Any field added, removed or re-typed bumps `SCHEMA_VERSION`, amends this file, regenerates the golden files under `tests/golden/reports/`, re-exports `schemas/report-v1.json` (`uv run python scripts/export_schema.py`) and records the reason in the commit body. Models are frozen pydantic models with `extra="forbid"`; `Report.to_json()` is canonical (sorted keys, two-space indent, trailing newline) so the same input gives the same bytes; a test compares the exported JSON schema with the live one.

## Finding

| Field | Type | Meaning |
|-------|------|---------|
| `id` | string | stable within a report, `f-<n>` |
| `technique_id` | string | from the registry, `pdf.text.low_contrast` |
| `status` | `possible` or `confirmed` | a View C candidate is possible until View B or a self-proving mechanism confirms it |
| `page` | int or null | 1-based; null for document-level (metadata) |
| `bbox` | [x0, y0, x1, y1] in PDF points or null | region on the page |
| `extracted_text` | string | what View A returned for the region (redacted to a length cap when `--redact`) |
| `render_crop` | data URI or `{ "none": "<reason>" }` | the rendered region; reason when absent (document-level, redacted, fast tier) |
| `why_hidden` | string | the plain-language sentence from the registry |
| `mechanism` | string | the exact object or element: "Tr 3 at content stream byte 1214 of page 1 object 12", "w:vanish on run 7 of paragraph 3" |
| `reproduce` | string | a one-line command: `paperglass show --object 12 file.pdf`, `qpdf --qdf --object-streams=disable file.pdf - | sed -n ...` |
| `severity` | `info`, `low`, `medium`, `high`, `critical` | after the severity class and profile |
| `severity_class` | `instruction`, `data`, `benign-hidden`, `structure-only` | the class that produced the severity |
| `confidence` | float 0 to 1 | per finding |
| `views` | list of `A`, `B`, `C` | which views contributed |
| `stage` | int | highest cascade stage that touched it |
| `atr_rule` | string or null | `ATR-2026-00515` where a phrase-level rule fits; null for structural techniques (proposal pending) |
| `extractor` | string | the View A backend that produced `extracted_text` |

## Report

| Field | Meaning |
|-------|---------|
| `schema_version` | 1 |
| `tool_version` | `paperglass` version |
| `rule_versions` | map of technique id to rule version |
| `input_sha256` | hash of the input bytes |
| `input_type` | sniffed type |
| `extractor` | default View A backend used |
| `tier` | fast, standard, deep |
| `profile` | default, resume, peer-review, rag-ingest |
| `page_count`, `pages_render_verified`, `dpi` | what was checked |
| `verdict` | `clean`, `benign-hidden`, `suspicious`, `malicious` |
| `severity_counts` | map of severity to count, confirmed findings only |
| `findings` | list |
| `parse_failures` | list of `ParseFailure` (stage, parser, reason in crash, timeout, memory, cpu, size, pages, zip_ratio, recursion, message); a parser crash is reported, never raised |
| `network_used` | list of named network features used (empty by default) |
| `timing_ms` | per stage |

## Verdict rules (default profile)

| Condition (confirmed findings only) | Verdict |
|-------------------------------------|---------|
| any `high` or `critical` | `malicious` |
| any `medium` | `suspicious` |
| only `benign-hidden` and `info` | `benign-hidden` |
| none | `clean` |
| any `parse_failures` and nothing above | `suspicious` (a file the scanner cannot read is a file a person could not review) |

There is no numeric score. A 0 to 100 number invites ranking people and contradicts "never decides an outcome for a person". Policy objects and adapters act on the verdict and the severity counts.

## Severity classes

| Class | Default severity | Escalation |
|-------|------------------|------------|
| `instruction` | high | critical when the text names an action for the model ("rank first", "ignore", "output") |
| `data` | medium | high when hidden text contradicts visible text (hidden "10 years" against visible "3 years") or duplicates a supplied job description in the resume profile |
| `benign-hidden` | info | never escalates; a constraint violation reclassifies the run to the hiding technique's class |
| `structure-only` | info | never drives a verdict alone; the deep tier may confirm and reclassify |

## CleanResult (v0.4.0)

`text`, `runs` (each with `provenance` in `visible-confirmed`, `benign-hidden`, `structure-only`, `removed`), `words_kept`, `words_removed`, `fidelity` (0 to 1), `policy_applied`, `report` (the Report above).

## Receipt (MCP, v0.4.0)

`input_sha256`, `verdict`, `severity_counts`, `rule_versions`, `tool_version`, `pages_render_verified`, `issued_at`.
