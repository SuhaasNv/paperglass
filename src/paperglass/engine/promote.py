"""Promotion: a View C candidate is possible until View B or a self-proving mechanism
confirms it. Stage 1 looks for ink; stage 2 reads the crop; a candidate the raster
contradicts is dropped, because the person can see that text.
"""

from __future__ import annotations

from dataclasses import dataclass

from paperglass.detectors import Candidate
from paperglass.engine.profile import Profile
from paperglass.models import FindingStatus, InkResult, OcrResult, PageRaster, RenderCrop
from paperglass.views.render import agreement, crop_data_uri, ink_check, ocr_available, ocr_crop


@dataclass(frozen=True)
class Promotion:
    status: FindingStatus | None
    """None means the candidate is dropped: the raster shows the text."""
    stage: int
    ink: InkResult | None
    ocr: OcrResult | None
    crop: RenderCrop
    benign_reason: str | None = None
    views: tuple[str, ...] = ("C",)


def promote(  # noqa: PLR0911  # one return per branch of the promotion table in VIEWS.md
    candidate: Candidate,
    raster: PageRaster | None,
    *,
    profile: Profile,
    use_ocr: bool,
    structure_only: bool = False,
) -> Promotion:
    """structure_only: ink on the page does not contradict the candidate (fonts, ActualText);
    it stays possible until stage 2 disagrees with what the model reads."""
    no_raster = RenderCrop(none_reason="no raster for this candidate")
    if candidate.self_proving:
        crop = crop_data_uri(raster, candidate.bbox) if raster and candidate.bbox else no_raster
        return Promotion(FindingStatus.CONFIRMED, 0, None, None, crop, views=("C",))
    if raster is None or candidate.bbox is None:
        reason = "fast tier or no bbox" if raster is None else "document-level finding"
        return Promotion(FindingStatus.POSSIBLE, 0, None, None, RenderCrop(none_reason=reason))
    ink = ink_check(raster, candidate.bbox, **_ink_thresholds(profile))
    crop = crop_data_uri(raster, candidate.bbox)
    if ink.classification == "invisible" and not structure_only:
        return Promotion(FindingStatus.CONFIRMED, 1, ink, None, crop, views=("B", "C"))
    if ink.classification == "visible" and not use_ocr:
        status = FindingStatus.POSSIBLE if structure_only else None
        return Promotion(status, 1, ink, None, crop, views=("B", "C"))
    if not use_ocr or not ocr_available():
        return Promotion(FindingStatus.POSSIBLE, 1, ink, None, crop, views=("B", "C"))
    read = ocr_crop(raster, candidate.bbox)
    score = agreement(candidate.extracted_text, read.text)
    if score >= profile.thresholds.ocr_agreement_benign and ink.classification == "visible":
        status = FindingStatus.POSSIBLE if structure_only else None
        return Promotion(status, 2, ink, read, crop, views=("B", "C"))
    if score < profile.thresholds.ocr_agreement_hidden:
        return Promotion(FindingStatus.CONFIRMED, 2, ink, read, crop, views=("B", "C"))
    return Promotion(FindingStatus.POSSIBLE, 2, ink, read, crop, views=("B", "C"))


def ocr_layer_is_benign(
    candidate: Candidate, raster: PageRaster | None, *, profile: Profile, use_ocr: bool
) -> OcrResult | None:
    """A render-mode-3 run whose OCR reading matches the extracted text is a scan's OCR layer."""
    if candidate.technique_id != "pdf.render.mode" or raster is None or candidate.bbox is None:
        return None
    if not use_ocr or not ocr_available():
        return None
    read = ocr_crop(raster, candidate.bbox)
    if agreement(candidate.extracted_text, read.text) >= profile.allowlist.ocr_layer_min_agreement:
        return read
    return None


def _ink_thresholds(profile: Profile) -> dict[str, float]:
    thresholds = profile.thresholds
    return {
        "contrast_threshold": thresholds.contrast,
        "visible_fraction": thresholds.ink_fraction_visible,
        "invisible_fraction": thresholds.ink_fraction_invisible,
    }
