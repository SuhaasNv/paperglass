"""pdf.font.tounicode_mismatch: the CMap tells the model different letters than the glyphs
named in the encoding. Static probe; the glyph arbiter (US-087) confirms by rendering."""

from __future__ import annotations

from collections.abc import Iterable

from fontTools.agl import toUnicode

from paperglass.detectors.base import Candidate, Detector
from paperglass.detectors.registry import SeverityDefault, technique
from paperglass.models import PdfFontInfo
from paperglass.views.context import PageContext

WIN_ANSI_ASCII = {code: chr(code) for code in range(0x20, 0x7F)}
MIN_MISMATCHES = 1


def expected_text(font: PdfFontInfo, code: int) -> str | None:
    """What the encoding says the glyph at this code is, for simple fonts only."""
    if font.is_type0 or font.is_type3:
        return None
    if code in font.differences:
        return toUnicode(font.differences[code]) or None
    if font.encoding in ("WinAnsiEncoding", "StandardEncoding", "MacRomanEncoding", None):
        return WIN_ANSI_ASCII.get(code)
    return None


def mismatches(font: PdfFontInfo) -> list[tuple[int, str, str]]:
    found: list[tuple[int, str, str]] = []
    for code, declared in sorted(font.to_unicode_map.items()):
        expected = expected_text(font, code)
        if expected is None or not declared:
            continue
        if declared != expected:
            found.append((code, expected, declared))
    return found


@technique(
    id="pdf.font.tounicode_mismatch",
    formats=("pdf",),
    views=("C",),
    stage=0,
    severity_class=SeverityDefault.STRUCTURE_ONLY,
    explanation="The font tells the model different letters than it draws",
    threshold="ToUnicode CMap maps a glyph to a code point whose canonical shape differs from the painted glyph; possible at stage 0, confirmed by the glyph arbiter",
    rule_version="1",
    release="v0.1.0",
)
class ToUnicodeMismatchDetector(Detector):
    def probe(self, ctx: PageContext) -> Iterable[Candidate]:
        if ctx.structure is None:
            return ()
        used = {obj.font_resource for obj in ctx.structure.text_objects if obj.text.strip()}
        found: list[Candidate] = []
        for font in ctx.structure.fonts:
            if font.resource not in used:
                continue
            bad = mismatches(font)
            if len(bad) < MIN_MISMATCHES:
                continue
            sample = "; ".join(
                f"code {code:#04x} draws {expected!r} but declares {declared!r}"
                for code, expected, declared in bad[:4]
            )
            affected = [
                obj for obj in ctx.structure.text_objects if obj.font_resource == font.resource
            ]
            first = affected[0] if affected else None
            found.append(
                Candidate(
                    technique_id="pdf.font.tounicode_mismatch",
                    page=ctx.page_number,
                    bbox=first.bbox if first else None,
                    extracted_text=" ".join(obj.text for obj in affected)[:500],
                    mechanism=(
                        f"font /{font.resource} ({font.base_font or 'unnamed'}"
                        f"{', object ' + str(font.object_number) if font.object_number else ''}): "
                        f"{len(bad)} ToUnicode entries disagree with the encoding: {sample}"
                    ),
                    reproduce=f"paperglass show --page {ctx.page_number} --font {font.resource} FILE",
                    confidence=0.92 if len(bad) >= 2 else 0.85,
                )
            )
        return found
