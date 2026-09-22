"""Stage 1: does the raster carry ink where the extractor says there is text?

No OCR. For a region we measure, against the local background, how many pixels differ
by more than the contrast threshold, the largest difference, and the variance. The
thresholds are the ones in THREATS.md (contrast 24/255) and UNITES (ink 1.5 percent).
"""

from __future__ import annotations

import io
from functools import lru_cache

import numpy as np
from PIL import Image

from paperglass.models import BBox
from paperglass.models.raster import InkClass, InkResult, PageRaster

CONTRAST_THRESHOLD = 24 / 255
INK_FRACTION_VISIBLE = 0.015
INK_FRACTION_INVISIBLE = 0.002
MARGIN_PT = 4.0
MIN_PIXELS = 4


@lru_cache(maxsize=64)
def _luminance(png: bytes) -> np.ndarray:
    """The page as a float32 luminance array in 0 to 1, cached per raster."""
    image = Image.open(io.BytesIO(png)).convert("L")
    return np.asarray(image, dtype=np.float32) / 255.0


def to_pixels(raster: PageRaster, bbox: BBox, pad_pt: float = 0.0) -> tuple[int, int, int, int]:
    """PDF points (origin bottom-left) to raster pixels (origin top-left), clamped to the page."""
    scale = raster.dpi / 72.0
    x0 = int(np.floor((bbox.x0 - pad_pt) * scale))
    x1 = int(np.ceil((bbox.x1 + pad_pt) * scale))
    y0 = int(np.floor((raster.height_pt - bbox.y1 - pad_pt) * scale))
    y1 = int(np.ceil((raster.height_pt - bbox.y0 + pad_pt) * scale))
    x0, x1 = max(0, min(raster.width_px, x0)), max(0, min(raster.width_px, x1))
    y0, y1 = max(0, min(raster.height_px, y0)), max(0, min(raster.height_px, y1))
    return x0, y0, x1, y1


def ink_check(raster: PageRaster, bbox: BBox) -> InkResult:
    """Classify a region visible, invisible or uncertain from the raster alone."""
    page = _luminance(raster.png)
    x0, y0, x1, y1 = to_pixels(raster, bbox)
    region = page[y0:y1, x0:x1]
    pixels = int(region.size)
    background = _background(page, raster, bbox)
    if pixels < MIN_PIXELS:
        return InkResult(
            bbox=bbox,
            ink_fraction=0.0,
            contrast=0.0,
            variance=0.0,
            background=background,
            classification="invisible",
            pixels=pixels,
        )
    difference = np.abs(region - background)
    ink_fraction = float(np.mean(difference > CONTRAST_THRESHOLD))
    contrast = float(np.max(difference))
    variance = float(np.var(region))
    classification: InkClass
    if ink_fraction >= INK_FRACTION_VISIBLE and contrast > CONTRAST_THRESHOLD:
        classification = "visible"
    elif ink_fraction <= INK_FRACTION_INVISIBLE or contrast <= CONTRAST_THRESHOLD:
        classification = "invisible"
    else:
        classification = "uncertain"
    return InkResult(
        bbox=bbox,
        ink_fraction=ink_fraction,
        contrast=min(1.0, contrast),
        variance=variance,
        background=background,
        classification=classification,
        pixels=pixels,
    )


def _background(page: np.ndarray, raster: PageRaster, bbox: BBox) -> float:
    """Median luminance of a ring around the region; the page median when the ring is empty."""
    ox0, oy0, ox1, oy1 = to_pixels(raster, bbox, pad_pt=MARGIN_PT)
    ix0, iy0, ix1, iy1 = to_pixels(raster, bbox)
    outer = page[oy0:oy1, ox0:ox1]
    if outer.size == 0:
        return float(np.median(page)) if page.size else 1.0
    mask = np.ones(outer.shape, dtype=bool)
    mask[iy0 - oy0 : iy1 - oy0, ix0 - ox0 : ix1 - ox0] = False
    ring = outer[mask]
    if ring.size == 0:
        return float(np.median(page)) if page.size else 1.0
    return float(np.median(ring))
