"""text.unicode.invisible: characters that carry text but draw nothing."""

from __future__ import annotations

import unicodedata
from collections.abc import Iterable

from paperglass.detectors.base import Candidate, Detector
from paperglass.detectors.registry import SeverityDefault, technique
from paperglass.views.context import PageContext

TAG_BLOCK = range(0xE0000, 0xE0080)
ZERO_WIDTH = frozenset({0x200B, 0x200C, 0x200D, 0x2060, 0xFEFF, 0x180E})
BIDI_CONTROLS = (
    frozenset(range(0x202A, 0x202F)) | frozenset(range(0x2066, 0x206A)) | {0x200E, 0x200F}
)
MIN_RUN_HITS = 1


def invisible_code_points(text: str) -> list[tuple[int, str]]:
    """Every invisible or direction-overriding code point in the text, with its name."""
    hits: list[tuple[int, str]] = []
    for char in text:
        point = ord(char)
        if point in TAG_BLOCK:
            hits.append((point, "tag character"))
        elif point in ZERO_WIDTH:
            hits.append((point, "zero-width character"))
        elif point in BIDI_CONTROLS:
            hits.append((point, "bidirectional override"))
        elif unicodedata.category(char) == "Cf" and point not in (0x00AD,):
            hits.append((point, "format character"))
    return hits


def decode_tags(text: str) -> str:
    """The ASCII hidden in tag characters (U+E0041 is 'A'), for the report."""
    return "".join(
        chr(ord(c) - 0xE0000)
        for c in text
        if ord(c) in TAG_BLOCK and 0x20 <= ord(c) - 0xE0000 < 0x7F
    )


@technique(
    id="text.unicode.invisible",
    formats=("any",),
    views=("A",),
    stage=0,
    severity_class=SeverityDefault.DATA,
    explanation="Characters that carry text but draw nothing: tag characters, zero-width joiners, direction overrides, look-alike letters",
    threshold="U+E0000 block, U+200B to U+200F, U+202A to U+202E, U+2066 to U+2069, confusables outside the document's script",
    atr_rule="ATR-2026-00515",
    rule_version="1",
    release="v0.1.0",
)
class InvisibleUnicodeDetector(Detector):
    def probe(self, ctx: PageContext) -> Iterable[Candidate]:
        found: list[Candidate] = []
        for index, run in enumerate(ctx.runs):
            hits = invisible_code_points(run.text)
            if len(hits) < MIN_RUN_HITS:
                continue
            kinds = sorted({kind for _, kind in hits})
            sample = ", ".join(f"U+{point:04X}" for point, _ in hits[:5])
            hidden = decode_tags(run.text)
            found.append(
                Candidate(
                    technique_id="text.unicode.invisible",
                    page=ctx.page_number,
                    bbox=run.bbox,
                    extracted_text=hidden or run.text,
                    mechanism=(
                        f"{len(hits)} invisible code point(s) ({', '.join(kinds)}: {sample}) in run "
                        f"{index} of page {ctx.page_number}"
                        + (f"; decodes to {hidden!r}" if hidden else "")
                    ),
                    reproduce=f"paperglass show --page {ctx.page_number} --run {index} --codepoints FILE",
                    confidence=0.98 if any(p in TAG_BLOCK for p, _ in hits) else 0.9,
                )
            )
        return found
