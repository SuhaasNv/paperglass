"""pdf.render.mode: text render mode 3 (paint nothing) or 7 (clip only)."""

from __future__ import annotations

from paperglass.detectors.base import Candidate
from paperglass.detectors.pdf._common import TextObjectDetector, preview, reproduce
from paperglass.detectors.registry import SeverityDefault, technique
from paperglass.models import PdfTextObject
from paperglass.views.context import PageContext

INVISIBLE_MODES = frozenset({3, 7})


@technique(
    id="pdf.render.mode",
    formats=("pdf",),
    views=("B", "C"),
    stage=1,
    self_proving=True,
    severity_class=SeverityDefault.DATA,
    explanation="Text drawn in a mode that paints nothing (mode 3) or only sets a clip (mode 7)",
    threshold="`Tr 3` or `Tr 7` with extractable text; OCR text layers on scans are benign-hidden when they match the render",
    rule_version="1",
    release="v0.1.0",
)
class RenderModeDetector(TextObjectDetector):
    def check(self, ctx: PageContext, obj: PdfTextObject) -> Candidate | None:
        if obj.render_mode not in INVISIBLE_MODES:
            return None
        return Candidate(
            technique_id="pdf.render.mode",
            page=ctx.page_number,
            bbox=obj.bbox,
            extracted_text=obj.text,
            mechanism=(
                f"Tr {obj.render_mode} in force at instruction {obj.instruction} of the "
                f"page {ctx.page_number} content stream; text {preview(obj.text)!r}"
            ),
            reproduce=reproduce(ctx, obj),
            confidence=0.98,
            self_proving=True,
        )
