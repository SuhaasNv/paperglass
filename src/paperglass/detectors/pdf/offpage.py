"""pdf.text.offpage: text placed outside the visible page or fully clipped away."""

from __future__ import annotations

from paperglass.detectors.base import Candidate
from paperglass.detectors.pdf._common import PAINTING_MODES, TextObjectDetector, preview, reproduce
from paperglass.detectors.registry import SeverityDefault, technique
from paperglass.models import BBox, PdfTextObject
from paperglass.views.context import PageContext


def _outside(box: BBox, area: BBox) -> bool:
    return box.x1 <= area.x0 or box.x0 >= area.x1 or box.y1 <= area.y0 or box.y0 >= area.y1


def _empty(box: BBox) -> bool:
    return box.x1 <= box.x0 or box.y1 <= box.y0


@technique(
    id="pdf.text.offpage",
    formats=("pdf",),
    views=("B", "C"),
    stage=1,
    severity_class=SeverityDefault.DATA,
    explanation="Text placed outside the visible page or cut off by a clip",
    threshold="bbox outside MediaBox or CropBox, or fully clipped",
    rule_version="1",
    release="v0.1.0",
)
class OffPageDetector(TextObjectDetector):
    def check(self, ctx: PageContext, obj: PdfTextObject) -> Candidate | None:
        if obj.render_mode not in PAINTING_MODES or obj.bbox is None or ctx.structure is None:
            return None
        page = ctx.structure
        visible = page.crop_box or BBox(x0=0, y0=0, x1=page.width, y1=page.height)
        why: str | None = None
        if _outside(obj.bbox, visible):
            why = (
                f"bbox ({obj.bbox.x0:.0f}, {obj.bbox.y0:.0f}, {obj.bbox.x1:.0f}, {obj.bbox.y1:.0f}) "
                f"lies outside the visible page (0, 0, {visible.x1:.0f}, {visible.y1:.0f})"
            )
        elif obj.clip is not None and (_empty(obj.clip) or _outside(obj.bbox, obj.clip)):
            why = (
                f"clip ({obj.clip.x0:.0f}, {obj.clip.y0:.0f}, {obj.clip.x1:.0f}, {obj.clip.y1:.0f}) "
                f"excludes the text bbox"
            )
        if why is None:
            return None
        return Candidate(
            technique_id="pdf.text.offpage",
            page=ctx.page_number,
            bbox=obj.bbox,
            extracted_text=obj.text,
            mechanism=(
                f"{why} at instruction {obj.instruction} of the page {ctx.page_number} "
                f"content stream; text {preview(obj.text)!r}"
            ),
            reproduce=reproduce(ctx, obj),
            confidence=0.95,
        )
