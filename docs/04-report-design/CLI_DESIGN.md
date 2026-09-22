# CLI design

Built at US-036 (22 Sep 2026): `paperglass scan`, `fingerprint`, `show`, `version`, `profiles` (`src/paperglass/adapters/cli.py`, tests in `tests/adapters/test_cli.py`). `report` and `scan --report` landed at US-037 (22 Sep 2026); `clean` and `bench` land with their stories. `paperglass` (typer). Every command prints JSON with `--json`, human text otherwise. No telemetry. No network unless `--allow-network` (v0.4.0).

| Command | Release | What it does |
|---------|---------|--------------|
| `paperglass scan <file or dir> [--tier fast|standard|deep] [--profile name] [--redact] [--report out.html] [--sarif out.sarif] [--json]` | v0.1.0 (report v0.2.0, sarif v0.4.0) | Scans; prints the verdict, counts and findings; writes reports when asked; a directory scans every supported file and exits with the worst verdict |
| `paperglass fingerprint <file> [--extractors a,b,c]` | v0.1.0 | Runs stages 0 and 1 per installed extractor; prints a table of findings against extractors: which ones return each hidden run |
| `paperglass show <file> --page N --instruction I`, `--object N`, `--page N --font F`, `--page N --annotation I`, `--info`, `--xmp`, `--actions`, `--embedded`, `--page N --run I --ink`, `--run I --codepoints`, `--part P [--paragraph N --run I]` | v0.1.0 | Prints the raw object, instruction, font, annotation, metadata, action, run or OOXML element behind a finding (the reproduce path), through the sandbox |
| `paperglass report <file> [--out report.html]` | v0.2.0 | Scan plus HTML |
| `paperglass clean <file> [--policy pass|clean|block] [--substitute-ocr]` | v0.4.0 | Prints the subtractive clean text, the provenance summary and the fidelity line |
| `paperglass bench --corpus <name> --version <vN> [--detector module:callable]` | v0.3.0 | Runs the harness; writes a results file |
| `paperglass profiles` | v0.2.0 | Lists profiles and their thresholds |
| `paperglass version` | v0.1.0 | Tool version and rule versions |

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | clean or benign-hidden |
| 1 | suspicious |
| 2 | malicious |
| 3 | error (unreadable input, sandbox failure without any view, bad arguments) |

A directory scan returns the highest code among its files.

## Output rules

Human output: verdict line first, then severity counts, then one line per finding (technique sentence, page, status, mechanism). Findings sorted by severity then page. `--redact` blanks extracted text beyond 80 characters and drops crops outside findings. Colours in the terminal are decorative only; every severity has its label.
