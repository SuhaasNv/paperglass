# Instruction-likeness hook

## What it is

`text.instruction.hint` is a modifier, not a detector. It runs only on text that another finding has already established as hidden or structure-only, and it can only raise severity (data to instruction, high to critical). It can never create a finding, and a document with no hidden text is never touched by it.

## Why it is small on purpose

More than 90 percent of real injections are hidden data, not instructions (UNITES). A phrase list catches the loud minority; the mechanism detectors catch the rest. Phrase lists are also what adaptive attackers evade first, so nothing in the verdict may depend on one.

## Phrase packs

`src/paperglass/profiles/phrases/<name>.toml`: short lists of instruction patterns (imperatives addressed to a model, ranking and scoring verbs, "ignore previous", role claims), per profile. English only in v0.1.0; other languages are a community contribution after v1.0.0 (deferred by name in `SCOPE.md`).

## Plug-in interface

```python
class SeverityHint(Protocol):
    name: str
    version: str
    def score(self, text: str) -> float: ...   # 0 to 1, instruction-likeness
```

Registered by entry point `paperglass.hints`. Prompt Guard 2 (Llama 4 Community Licence, gated download) can be wired by the user as such a plug-in; core never imports it. Any plug-in used is named in the report under `rule_versions`.

## Deep tier (COULD)

An optional small vision model (Florence-2 MIT or SmolVLM2 Apache-2.0) for scans and low-contrast images, seconds per page, opt-in, never default, network only with `allow_network` for the first download. Its evaluation set lives in `AI_EVALUATION.md` if it is built.
