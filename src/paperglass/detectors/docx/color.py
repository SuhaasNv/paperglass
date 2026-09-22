"""docx.run.color: run colour within 24/255 of the page or shading colour."""

from __future__ import annotations

from collections.abc import Iterable

from paperglass.detectors.base import Candidate, Detector
from paperglass.detectors.docx._common import locate, preview, reproduce
from paperglass.detectors.registry import SeverityDefault, technique
from paperglass.models.docx import DocxRun, DocxStructure
from paperglass.views.context import PageContext


def _hex_grey(value: str | None) -> float | None:
    if not value or len(value) != 6:
        return None
    try:
        r, g, b = (int(value[i : i + 2], 16) / 255.0 for i in (0, 2, 4))
    except ValueError:
        return None
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def background_of(run: DocxRun, doc: DocxStructure) -> float:
    if run.shading_fill and run.shading_fill.lower() != "auto":
        return _hex_grey(run.shading_fill) or 1.0
    if run.highlight and run.highlight.lower() not in ("none", "white"):
        return 0.5
    if doc.page_background:
        return _hex_grey(doc.page_background) or 1.0
    return 1.0


@technique(
    id="docx.run.color",
    formats=("docx",),
    views=("B", "C"),
    stage=0,
    self_proving=True,  # no DOCX raster in v0.1.0: the colour rule stands on its own
    severity_class=SeverityDefault.DATA,
    explanation="Text coloured to match the page",
    threshold="run colour within 24/255 of the page or shading colour",
    rule_version="1",
    release="v0.1.0",
)
class ColorRunDetector(Detector):
    def probe(self, ctx: PageContext) -> Iterable[Candidate]:
        if ctx.docx is None:
            return ()
        found: list[Candidate] = []
        for run in ctx.docx.runs:
            if run.grey is None or not run.text.strip() or run.vanish:
                continue
            background = background_of(run, ctx.docx) or 1.0
            if abs(run.grey - background) > ctx.profile.thresholds.contrast:
                continue
            found.append(
                Candidate(
                    technique_id="docx.run.color",
                    page=1,
                    extracted_text=run.text,
                    mechanism=(
                        f"w:color {run.color} (grey {run.grey:.2f}) against background grey "
                        f"{background:.2f} on {locate(run)}; text {preview(run.text)!r}"
                    ),
                    reproduce=reproduce(run),
                    confidence=0.95,
                    self_proving=True,
                )
            )
        return found
