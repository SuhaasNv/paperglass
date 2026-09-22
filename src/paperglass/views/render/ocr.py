"""Stage 2: OCR on crops only, behind the optional ocr extra.

OCR runs in the parent process on rasters Paperglass produced itself (never on the
input file), which is why it is not sandboxed: the pixels are ours. The engine is
RapidOCR (ONNX); when the extra is not installed, stage 2 is skipped and the report
says so.
"""

from __future__ import annotations

from functools import lru_cache
from importlib.metadata import PackageNotFoundError, version

import numpy as np
from rapidfuzz import fuzz

from paperglass.models import BBox
from paperglass.models.raster import OcrResult, PageRaster
from paperglass.views.render.crops import crop_image

ENGINE = "rapidocr-onnxruntime"


def ocr_available() -> bool:
    try:
        version(ENGINE)
    except PackageNotFoundError:
        return False
    return True


@lru_cache(maxsize=1)
def _engine() -> object:
    from rapidocr_onnxruntime import RapidOCR  # noqa: PLC0415  # optional extra

    return RapidOCR()


def ocr_crop(raster: PageRaster, bbox: BBox) -> OcrResult:
    """Read the text in one region. Returns an empty string when nothing is read."""
    image = crop_image(raster, bbox)
    result, _ = _engine()(np.asarray(image))  # type: ignore[operator]  # RapidOCR is untyped
    if not result:
        return OcrResult(text="", confidence=0.0, engine=ENGINE)
    texts = [str(item[1]) for item in result]
    scores = [float(item[2]) for item in result]
    return OcrResult(
        text=" ".join(texts), confidence=min(1.0, sum(scores) / len(scores)), engine=ENGINE
    )


def agreement(extracted: str, read: str) -> float:
    """0 to 1: how much of the extracted text OCR confirmed (partial ratio, case-folded)."""
    if not extracted.strip():
        return 1.0
    if not read.strip():
        return 0.0
    return float(fuzz.partial_ratio(extracted.casefold(), read.casefold())) / 100.0
