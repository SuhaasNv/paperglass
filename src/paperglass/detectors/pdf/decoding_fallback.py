"""pdf.font.decoding_fallback: a font an extractor cannot decode reliably, so the model may
read garbage or the wrong words. Informational; TeX Type 3 fonts are the known benign case."""

from __future__ import annotations

from collections.abc import Iterable

from paperglass.detectors.base import Candidate, Detector
from paperglass.detectors.registry import SeverityDefault, technique
from paperglass.models import PdfFontInfo
from paperglass.views.context import PageContext


def undecodable(font: PdfFontInfo) -> str | None:
    if font.is_type3 and not font.has_to_unicode:
        return "Type 3 font without a ToUnicode CMap"
    if font.is_type0 and not font.has_to_unicode:
        return "composite (Type 0) font without a ToUnicode CMap"
    if font.symbolic and not font.has_to_unicode and not font.differences:
        return "symbolic font without a ToUnicode CMap or Differences"
    return None


@technique(
    id="pdf.font.decoding_fallback",
    formats=("pdf",),
    views=("C",),
    stage=0,
    severity_class=SeverityDefault.STRUCTURE_ONLY,
    explanation="A font the extractor cannot decode, so the model may read garbage or the wrong words",
    threshold="Type 3, composite or CID font without a usable ToUnicode; extractors disagree (`paperglass fingerprint`)",
    rule_version="1",
    release="v0.1.0",
)
class DecodingFallbackDetector(Detector):
    def probe(self, ctx: PageContext) -> Iterable[Candidate]:
        if ctx.structure is None:
            return ()
        used = {obj.font_resource for obj in ctx.structure.text_objects if obj.text.strip()}
        found: list[Candidate] = []
        for font in ctx.structure.fonts:
            reason = undecodable(font)
            if reason is None or font.resource not in used:
                continue
            affected = [o for o in ctx.structure.text_objects if o.font_resource == font.resource]
            first = affected[0] if affected else None
            found.append(
                Candidate(
                    technique_id="pdf.font.decoding_fallback",
                    page=ctx.page_number,
                    bbox=first.bbox if first else None,
                    extracted_text=" ".join(o.text for o in affected)[:500],
                    mechanism=f"font /{font.resource} ({font.base_font or 'unnamed'}) is a {reason}",
                    reproduce=f"paperglass show --page {ctx.page_number} --font {font.resource} FILE",
                    confidence=0.92,
                )
            )
        return found
