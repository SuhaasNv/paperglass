"""Render once per page, inside the sandbox, at the dpi the page needs."""

from __future__ import annotations

from dataclasses import dataclass

from paperglass.ingest import Limits, run_sandboxed
from paperglass.models import DocumentStructure, ParseFailure
from paperglass.models.raster import PageRaster
from paperglass.parsers import pdf_render

DEFAULT_DPI = 150
SMALL_FONT_DPI = 200
SMALL_FONT_PT = 6.0


def choose_dpi(structure: DocumentStructure | None) -> int:
    """150 dpi, or 200 when any text object on any page is under 6 pt (VIEWS.md)."""
    if structure is None:
        return DEFAULT_DPI
    for page in structure.pages:
        for obj in page.text_objects:
            if obj.font_size is not None and 0 < obj.font_size < SMALL_FONT_PT:
                return SMALL_FONT_DPI
    return DEFAULT_DPI


@dataclass(frozen=True)
class RenderOutcome:
    rasters: tuple[PageRaster, ...]
    failure: ParseFailure | None
    dpi: int


def render_document(
    data: bytes,
    *,
    limits: Limits,
    numbers: tuple[int, ...],
    dpi: int,
    stage: int = 1,
) -> RenderOutcome:
    if not numbers:
        return RenderOutcome((), None, dpi)
    result = run_sandboxed(
        pdf_render.render_pages,
        (data, dpi, numbers),
        limits=limits,
        parser="pypdfium2",
        stage=stage,
    )
    if result.failure is not None or result.value is None:
        failure = result.failure or ParseFailure(
            stage=stage, parser="pypdfium2", reason="crash", message="no raster returned"
        )
        return RenderOutcome((), failure, dpi)
    return RenderOutcome(result.value, None, dpi)
