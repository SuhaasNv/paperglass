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


def _area(box: BBox) -> float:
    return max(0.0, box.x1 - box.x0) * max(0.0, box.y1 - box.y0)


def _intersection(a: BBox, b: BBox) -> float:
    width = min(a.x1, b.x1) - max(a.x0, b.x0)
    height = min(a.y1, b.y1) - max(a.y0, b.y0)
    return width * height if width > 0 and height > 0 else 0.0


def _overlap(run: BBox, finding: BBox) -> float:
    """The share of the run's box inside the finding's: the gate."""
    area = _area(run)
    return _intersection(run, finding) / area if area > 0 else 0.0


def _closeness(run: BBox, finding: BBox) -> float:
    """Intersection over union: the tie-break, so the finding that fits the run best wins."""
    union = _area(run) + _area(finding) - _intersection(run, finding)
    return _intersection(run, finding) / union if union > 0 else 0.0


def _finding_for(
    text: str, bbox: BBox | None, page: int, findings: list[Finding]
) -> Finding | None:
    best: Finding | None = None
    best_overlap = 0.0
    by_text: Finding | None = None
    for finding in findings:
        if finding.page != page or finding.status is not FindingStatus.CONFIRMED:
            continue
        if bbox is not None and finding.bbox is not None:
            if _overlap(bbox, finding.bbox) < OVERLAP:
                continue
            fit = _closeness(bbox, finding.bbox)
            if fit > best_overlap:
                best, best_overlap = finding, fit
        elif by_text is None and text.strip() and text.strip() in finding.extracted_text:
            by_text = finding
    return best or by_text


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
