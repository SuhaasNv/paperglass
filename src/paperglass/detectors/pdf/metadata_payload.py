"""pdf.metadata.payload: free text hidden in the Info dictionary or the XMP packet."""

from __future__ import annotations

from collections.abc import Iterable

from paperglass.detectors.base import Candidate, Detector
from paperglass.detectors.registry import SeverityDefault, technique
from paperglass.views.context import PageContext

LONG_VALUE = 200
"""An Info value longer than this is free text, not a title or an author."""
STANDARD_KEYS = frozenset(
    {
        "Title",
        "Author",
        "Subject",
        "Keywords",
        "Creator",
        "Producer",
        "CreationDate",
        "ModDate",
        "Trapped",
    }
)
XMP_LONG = 20_000


@technique(
    id="pdf.metadata.payload",
    formats=("pdf",),
    views=("C",),
    stage=0,
    severity_class=SeverityDefault.DATA,
    explanation="Text hidden in the file's properties or XMP metadata",
    threshold="Info dictionary or XMP packet contains instruction-like or long free text",
    atr_rule="ATR-2026-00515",
    rule_version="1",
    release="v0.1.0",
)
class MetadataPayloadDetector(Detector):
    """Document-level: runs once, on page 1, so the report carries a single finding."""

    def probe(self, ctx: PageContext) -> Iterable[Candidate]:
        if ctx.page_number != 1 or ctx.document is None:
            return ()
        found: list[Candidate] = []
        for key, value in sorted(ctx.document.metadata.info.items()):
            long = len(value) > LONG_VALUE
            odd_key = key not in STANDARD_KEYS
            multiline = "\n" in value
            if not (long or multiline or (odd_key and len(value) > 40)):
                continue
            reason = (
                "long free text" if long else "line breaks" if multiline else "a non-standard key"
            )
            found.append(
                Candidate(
                    technique_id="pdf.metadata.payload",
                    page=None,
                    extracted_text=value,
                    mechanism=f"Info dictionary key /{key} carries {reason} ({len(value)} characters)",
                    reproduce="paperglass show --info FILE",
                    confidence=0.92 if long else 0.7,
                )
            )
        xmp = ctx.document.metadata
        if xmp.xmp_length > XMP_LONG and xmp.xmp_text:
            found.append(
                Candidate(
                    technique_id="pdf.metadata.payload",
                    page=None,
                    extracted_text=xmp.xmp_text,
                    mechanism=f"XMP packet is {xmp.xmp_length} characters long",
                    reproduce="paperglass show --xmp FILE",
                    confidence=0.6,
                )
            )
        return found
