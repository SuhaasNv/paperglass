# Red Kit (v0.5.0)

A deterministic generator of injected samples and matched controls, so the benchmark grows faster than the attacks and every technique has a reproducible sample.

- Formats: PDF (reportlab) and DOCX (python-docx). Images deferred.
- Determinism: `paperglass redkit generate --technique pdf.text.low_contrast --seed 42 --out dir/` writes `pdf.text.low_contrast-42-positive.pdf` and `pdf.text.low_contrast-42-negative.pdf` (the matched control: same base document, no injection). The seed is in the file name; the same seed gives byte-identical output for the same tool version.
- Payloads: drawn from a small pack of data-injection and instruction-injection strings, never real personal data, labelled `injection_kind`.
- Adding a technique: one generator module under `src/paperglass/redkit/<format>/<slug>.py` registered with `@generator(technique_id=...)` plus the fixture pair it produces at a fixed seed; the benchmark version bumps to include it.
- Red Kit samples are labelled ours in the index and never produce a headline number for Paperglass.
