"""pdf.layer.hidden: text inside an optional content group that is OFF by default."""

from __future__ import annotations

from paperglass.detectors.base import Candidate
from paperglass.detectors.pdf._common import TextObjectDetector, preview, reproduce
from paperglass.detectors.registry import SeverityDefault, technique
from paperglass.models import PdfTextObject
from paperglass.views.context import PageContext


@technique(
    id="pdf.layer.hidden",
    formats=("pdf",),
    views=("C",),
    stage=0,
    self_proving=True,
    severity_class=SeverityDefault.DATA,
    explanation="Text on a layer that is switched off",
    threshold="optional content group in the default OFF array, or `/OC` marked content whose OCG is OFF",
    rule_version="1",
    release="v0.1.0",
)
class HiddenLayerDetector(TextObjectDetector):
    def check(self, ctx: PageContext, obj: PdfTextObject) -> Candidate | None:
        if not obj.ocg_hidden:
            return None
        return Candidate(
            technique_id="pdf.layer.hidden",
            page=ctx.page_number,
            bbox=obj.bbox,
            extracted_text=obj.text,
            mechanism=(
                f"optional content group {obj.ocg!r} is in the default OFF array; text at "
                f"instruction {obj.instruction} of the page {ctx.page_number} content stream: "
                f"{preview(obj.text)!r}"
            ),
            reproduce=reproduce(ctx, obj),
            confidence=0.98,
            self_proving=True,
        )
