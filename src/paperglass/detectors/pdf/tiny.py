"""pdf.text.tiny: effective font size below 2 pt, or zero."""

from __future__ import annotations

from paperglass.detectors.base import Candidate
from paperglass.detectors.pdf._common import PAINTING_MODES, TextObjectDetector, preview, reproduce
from paperglass.detectors.registry import SeverityDefault, technique
from paperglass.models import PdfTextObject
from paperglass.views.context import PageContext

TINY_PT = 2.0


@technique(
    id="pdf.text.tiny",
    formats=("pdf",),
    views=("B", "C"),
    stage=1,
    severity_class=SeverityDefault.DATA,
    explanation="Text too small for a person to read",
    threshold="effective font size after the CTM below 2 pt, or zero",
    rule_version="1",
    release="v0.1.0",
)
class TinyTextDetector(TextObjectDetector):
    def check(self, ctx: PageContext, obj: PdfTextObject) -> Candidate | None:
        if obj.render_mode not in PAINTING_MODES:
            return None
        size = obj.font_size or 0.0
        if size >= TINY_PT:
            return None
        return Candidate(
            technique_id="pdf.text.tiny",
            page=ctx.page_number,
            bbox=obj.bbox,
            extracted_text=obj.text,
            mechanism=(
                f"effective font size {size:.2f} pt at instruction {obj.instruction} of the "
                f"page {ctx.page_number} content stream; text {preview(obj.text)!r}"
            ),
            reproduce=reproduce(ctx, obj),
            confidence=0.98 if size == 0 else 0.95,
        )
