"""pdf.text.opacity: fill alpha below 0.1 from an ExtGState."""

from __future__ import annotations

from paperglass.detectors.base import Candidate
from paperglass.detectors.pdf._common import PAINTING_MODES, TextObjectDetector, preview, reproduce
from paperglass.detectors.registry import SeverityDefault, technique
from paperglass.models import PdfTextObject
from paperglass.views.context import PageContext

ALPHA_THRESHOLD = 0.1


@technique(
    id="pdf.text.opacity",
    formats=("pdf",),
    views=("B", "C"),
    stage=1,
    severity_class=SeverityDefault.DATA,
    explanation="Text made almost transparent",
    threshold="ExtGState `ca` or `CA` below 0.1, or a blend mode that hides the text",
    rule_version="1",
    release="v0.1.0",
)
class OpacityDetector(TextObjectDetector):
    def check(self, ctx: PageContext, obj: PdfTextObject) -> Candidate | None:
        if obj.render_mode not in PAINTING_MODES or obj.fill_alpha >= ALPHA_THRESHOLD:
            return None
        return Candidate(
            technique_id="pdf.text.opacity",
            page=ctx.page_number,
            bbox=obj.bbox,
            extracted_text=obj.text,
            mechanism=(
                f"fill alpha {obj.fill_alpha:g} from an ExtGState at instruction {obj.instruction} "
                f"of the page {ctx.page_number} content stream; text {preview(obj.text)!r}"
            ),
            reproduce=reproduce(ctx, obj),
            confidence=0.95,
        )
