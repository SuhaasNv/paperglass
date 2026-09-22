"""View B: raster, ink check, OCR on crops, glyph arbiter (docs/03-architecture/VIEWS.md)."""

from paperglass.views.render.crops import crop_data_uri, crop_image
from paperglass.views.render.ink import ink_check, to_pixels
from paperglass.views.render.ocr import agreement, ocr_available, ocr_crop
from paperglass.views.render.raster import RenderOutcome, choose_dpi, render_document

__all__ = [
    "RenderOutcome",
    "agreement",
    "choose_dpi",
    "crop_data_uri",
    "crop_image",
    "ink_check",
    "ocr_available",
    "ocr_crop",
    "render_document",
    "to_pixels",
]
