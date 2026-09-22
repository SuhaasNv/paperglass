# Results and leaderboard

v0.3.0 to v1.0.0: a `results/` directory in this repository. A submission is a pull request adding `results/<detector>/<version>/<corpus>.json` produced by the harness, with the exact command and the hardware in the file. CI re-runs the command on a sample and refuses a file whose sample does not reproduce. `BENCHMARK.md` tables are generated from `results/`. A CI badge (`paperglass-bench: v1 passing`) can be earned by any detector whose results file is merged.

A moderated Hugging Face Space with a reviewed submission workflow is deferred to after v1.0.0 (US-076): it needs a reviewer, and the pull-request flow gives the same public good at a tenth of the cost.

Rules: results name the corpus version; a new corpus version never overwrites old results; a detector may submit once per version; the results file for Paperglass itself is produced by CI at each release.
