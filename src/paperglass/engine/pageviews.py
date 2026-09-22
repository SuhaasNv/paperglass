"""Page views for the report (US-043): every extracted run with a status, and a thumbnail.

A run is hidden when a confirmed finding covers it, benign-hidden when a benign-hidden finding
does, visible when the stage 1 ink check finds ink where it sits, and unverified otherwise (no
raster in the fast tier for DOCX and text, no position, or an undecided ink check).
"""

from __future__ import annotations

from paperglass.engine.profile import Profile
from paperglass.models import (
    BBox,
    Finding,
    FindingStatus,
    PageRaster,
    PageView,
    RenderCrop,
    RunStatus,
    RunView,
    SeverityClass,
)
from paperglass.views.context import PageContext
from paperglass.views.render import THUMBNAIL_PAGE_CAP, ink_check, thumbnail_data_uri

OVERLAP = 0.5
"""A run belongs to a finding when this share of its box, at least, lies inside the finding's."""


def _overlap(run: BBox, finding: BBox) -> float:
    width = min(run.x1, finding.x1) - max(run.x0, finding.x0)
    height = min(run.y1, finding.y1) - max(run.y0, finding.y0)
    if width <= 0 or height <= 0:
        return 0.0
    area = (run.x1 - run.x0) * (run.y1 - run.y0)
    return (width * height) / area if area > 0 else 0.0


def _finding_for(
    text: str, bbox: BBox | None, page: int, findings: list[Finding]
) -> Finding | None:
    for finding in findings:
        if finding.page != page or finding.status is not FindingStatus.CONFIRMED:
            continue
        if bbox is not None and finding.bbox is not None:
            if _overlap(bbox, finding.bbox) >= OVERLAP:
                return finding
        elif text.strip() and text.strip() in finding.extracted_text:
            return finding
    return None


def _status(finding: Finding | None, ink: str | None) -> RunStatus:
    if finding is not None:
        if finding.severity_class is SeverityClass.BENIGN_HIDDEN:
            return "benign-hidden"
        return "hidden"
    if ink == "visible":
        return "visible"
    return "unverified"


def build_page_views(
    pages: tuple[PageContext, ...],
    rasters: dict[int, PageRaster],
    findings: list[Finding],
    profile: Profile,
    *,
    redact: bool,
) -> tuple[PageView, ...]:
    thresholds = profile.thresholds
    views: list[PageView] = []
    for page in pages:
        raster = rasters.get(page.page_number)
        runs: list[RunView] = []
        for run in page.runs:
            finding = _finding_for(run.text, run.bbox, page.page_number, findings)
            ink: str | None = None
            if finding is None and raster is not None and run.bbox is not None:
                ink = ink_check(
                    raster,
                    run.bbox,
                    contrast_threshold=thresholds.contrast,
                    visible_fraction=thresholds.ink_fraction_visible,
                    invisible_fraction=thresholds.ink_fraction_invisible,
                ).classification
            text = run.text
            if redact and len(text) > 80:
                text = text[:77] + "..."
            runs.append(
                RunView(
                    text=text,
                    bbox=run.bbox,
                    status=_status(finding, ink),
                    finding_id=finding.id if finding is not None else None,
                )
            )
        if redact:
            thumbnail = RenderCrop(none_reason="redacted")
        elif raster is None:
            thumbnail = RenderCrop(none_reason="no raster for this page")
        elif page.page_number > THUMBNAIL_PAGE_CAP:
            thumbnail = RenderCrop(none_reason=f"page cap of {THUMBNAIL_PAGE_CAP} thumbnails")
        else:
            thumbnail = thumbnail_data_uri(raster)
        width = raster.width_pt if raster is not None else page.width
        height = raster.height_pt if raster is not None else page.height
        views.append(
            PageView(
                number=page.page_number,
                width_pt=width,
                height_pt=height,
                thumbnail=thumbnail,
                runs=tuple(runs),
            )
        )
    return tuple(views)
