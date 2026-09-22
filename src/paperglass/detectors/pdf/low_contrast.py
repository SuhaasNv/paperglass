"""pdf.text.low_contrast: fill colour within 24/255 of the page background."""

from __future__ import annotations

from paperglass.detectors.base import Candidate
from paperglass.detectors.pdf._common import PAINTING_MODES, TextObjectDetector, preview, reproduce
from paperglass.detectors.registry import SeverityDefault, technique
from paperglass.models import PdfTextObject
from paperglass.views.context import PageContext

BACKGROUND_GREY = 1.0
"""White; a page-background probe (stage 1) replaces this with the sampled background."""
CONTRAST_THRESHOLD = 24 / 255


@technique(
    id="pdf.text.low_contrast",
    formats=("pdf",),
    views=("B", "C"),
    stage=1,
    severity_class=SeverityDefault.DATA,
    explanation="Text painted in a colour a person cannot tell from the background",
    threshold="fill within 24/255 of the local background; fill colour from the text state",
    atr_rule="ATR-2026-00515",
    rule_version="1",
    release="v0.1.0",
)
class LowContrastDetector(TextObjectDetector):
    def check(self, ctx: PageContext, obj: PdfTextObject) -> Candidate | None:
        if obj.render_mode not in PAINTING_MODES or obj.fill is None or obj.fill.grey is None:
            return None
        distance = abs(obj.fill.grey - BACKGROUND_GREY)
        if distance > CONTRAST_THRESHOLD:
            return None
        components = " ".join(f"{c:g}" for c in obj.fill.components)
        return Candidate(
            technique_id="pdf.text.low_contrast",
            page=ctx.page_number,
            bbox=obj.bbox,
            extracted_text=obj.text,
            mechanism=(
                f"fill colour '{components} {obj.fill.operator}' (grey {obj.fill.grey:.3f}) "
                f"at instruction {obj.instruction} of the page {ctx.page_number} content stream; "
                f"text {preview(obj.text)!r}"
            ),
            reproduce=reproduce(ctx, obj),
            confidence=0.95 if distance <= CONTRAST_THRESHOLD / 2 else 0.85,
        )
