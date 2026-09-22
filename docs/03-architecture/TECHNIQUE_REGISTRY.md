# Technique registry

## Id naming

`<format>.<object>.<what>`: `pdf.text.low_contrast`, `pdf.render.mode`, `pdf.font.tounicode_mismatch`, `docx.run.vanish`, `text.unicode.invisible`, `html.dom.hidden`. Lowercase, dots, underscores inside a segment. `text.*` applies to every text format. An id is stable for life; renaming is a new id plus a deprecation entry, never an edit (`SCOPE.md`, disclosure in v0.5.0 adds the public `pg.` prefix as an alias).

## The `@technique` contract

```python
@technique(
    id="pdf.render.mode",
    formats=("pdf",),
    views=("C", "B"),
    stage=1,
    self_proving=True,
    severity_class="data",            # default class; the engine may escalate to instruction
    explanation="Text drawn in a mode that paints nothing (mode 3) or only sets a clip (mode 7).",
    threshold="Tr 3 or Tr 7 with extractable text",
    atr_rule=None,                    # or "ATR-2026-00515"
    rule_version="1",
)
class RenderModeDetector(Detector):
    def probe(self, ctx: PageContext) -> Iterable[Candidate]: ...
```

Rules:
- One module, one class, one id. A detector emits `Candidate` objects (View C) or `Finding` objects, never dicts.
- `explanation` is the single plain-language source shown in the report and checked against the `THREATS.md` row by a test; no jargon without the plain sentence beside it.
- `threshold` is documented text, and the numeric threshold it describes lives in the profile so that a profile can tighten it without a code change.
- `mechanism` and `reproduce` are filled by the detector for every candidate; the engine refuses a finding without them.
- `rule_version` bumps whenever the probe's logic changes; the report carries the map.
- A registered id must have `tests/fixtures/<format>/<id>/positive.*` and `negative.*` and a row in `THREATS.md`; `tests/unit/test_registry.py` fails on any mismatch.
- Instruction-likeness (`text.instruction.hint`) is a modifier, registered with `severity_class="modifier"`, and can never produce a finding on its own.

## Severity rules

Applied by the engine, not the detector: the class from the registration, escalation from content (contradiction, action verbs), the profile's overrides, the benign-hidden constraints. `structure-only` techniques (`pdf.font.decoding_fallback`, `pdf.order.split`) are pinned to info and never drive a verdict alone.

## Adding a technique

`CONTRIBUTING.md`, "Add a technique". Board: a story with label `technique`; `THREATS.md` row; ATR mapping or `none` with a reason; benchmark re-run with the false-positive rate in the pull request.
