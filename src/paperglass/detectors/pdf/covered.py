"""pdf.text.covered: the extractor returns text, the raster shows no ink, and nothing in the
text state explains it. A shape or an image was drawn on top."""

from __future__ import annotations

from collections.abc import Iterable

from paperglass.detectors.base import Candidate, Detector
from paperglass.detectors.pdf._common import PAINTING_MODES, preview
from paperglass.detectors.registry import SeverityDefault, technique
from paperglass.models import BBox, PageStructure, PdfTextObject
from paperglass.views.context import PageContext
from paperglass.views.render import ink_check

NEAR_WHITE = 1.0 - 24 / 255
ALPHA = 0.1
TINY_PT = 2.0


def overlaps(a: BBox, b: BBox) -> bool:
    return not (a.x1 <= b.x0 or a.x0 >= b.x1 or a.y1 <= b.y0 or a.y0 >= b.y1)


def explained_by_state(obj: PdfTextObject, page: PageStructure) -> bool:
    """True when another technique already accounts for the object being invisible."""
    if obj.render_mode not in PAINTING_MODES:
        return True
    if obj.fill is not None and obj.fill.grey is not None and obj.fill.grey >= NEAR_WHITE:
        return True
    if obj.fill_alpha < ALPHA or obj.ocg_hidden:
        return True
    if (obj.font_size or 0.0) < TINY_PT:
        return True
    visible = page.crop_box or BBox(x0=0, y0=0, x1=page.width, y1=page.height)
    return obj.bbox is not None and not overlaps(obj.bbox, visible)


@technique(
    id="pdf.text.covered",
    formats=("pdf",),
    views=("B",),
    stage=1,
    severity_class=SeverityDefault.DATA,
    explanation="Text hidden under a shape or image drawn on top of it",
    threshold="run extracted but no ink at its bbox after a later fill or image",
    rule_version="1",
    release="v0.1.0",
)
class CoveredTextDetector(Detector):
    def probe(self, ctx: PageContext) -> Iterable[Candidate]:
        if ctx.raster is None or ctx.structure is None:
            return ()
        found: list[Candidate] = []
        for index, run in enumerate(ctx.runs):
            if run.bbox is None or not run.text.strip():
                continue
            objects = [
                obj
                for obj in ctx.structure.text_objects
                if obj.bbox is not None and overlaps(obj.bbox, run.bbox)
            ]
            if objects and all(explained_by_state(obj, ctx.structure) for obj in objects):
                continue
            ink = ink_check(ctx.raster, run.bbox)
            if ink.classification != "invisible":
                continue
            found.append(
                Candidate(
                    technique_id="pdf.text.covered",
                    page=ctx.page_number,
                    bbox=run.bbox,
                    extracted_text=run.text,
                    mechanism=(
                        f"run {index} on page {ctx.page_number} is extracted as {preview(run.text)!r} "
                        f"but the raster shows no ink there (ink fraction {ink.ink_fraction:.4f}, "
                        f"background {ink.background:.2f}); a later fill or image covers it"
                    ),
                    reproduce=f"paperglass show --page {ctx.page_number} --run {index} --ink FILE",
                    confidence=0.92,
                )
            )
        return found
