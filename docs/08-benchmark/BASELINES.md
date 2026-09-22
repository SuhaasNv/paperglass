# Baselines

Each baseline is run with its default settings unless stated; every non-default flag is printed with the number. Commands are filled at US-054.

| Baseline | Licence | How run | Note |
|----------|---------|---------|------|
| PhantomLint | BSD-3 | its Docker image over the corpus; output diffed for any flagged span | phrase-gated: results reported with the gate and, if the code allows, with the gate disabled; 43 to 68 s per document, so a sampled run may be necessary and is stated |
| OpenDataLoader PDF | Apache-2.0 | `opendataloader-pdf` with its default content-safety filters on; a document counts as flagged when the filtered text differs from the unfiltered text | needs a JVM; a filter, not a detector, so the comparison is on detection only |
| DocFirewall | MIT | its CLI, if it installs cleanly on the CI image | if it does not, one sentence says so |
| Prompt Guard 2 (86M) | Llama 4 Community Licence, gated | run once on extracted text as the phrase-only control; the user downloads the weights | never a hard dependency; the number is the "text-only classifier" row |
| TF-IDF text-only | ours | shortcut audit only | never a baseline row |
