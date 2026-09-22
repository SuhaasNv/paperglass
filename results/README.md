# Results

One file per detector, version and corpus: `results/<detector>/<version>/<corpus>.json`, written by `paperglass bench run` (`docs/08-benchmark/HARNESS.md`). Each file carries the exact command that produced it, the hardware and the date; `paperglass bench verify` re-runs the command and refuses a file whose numbers do not reproduce (latency excluded, since that is hardware). CI runs the verification for Paperglass's own file on every push.

Submissions from other detectors are pull requests adding a file here (`docs/08-benchmark/LEADERBOARD.md`): the two-function adapter (`scan`, `version`) named as `module:function`, a reproducible command, and the corpus version. `BENCHMARK.md` tables are generated from this directory by `paperglass bench report`.

Corpora today: `fixtures` (the repository's own fixture pairs, synthetic, never a headline number). External corpora arrive with US-050 and US-051.
