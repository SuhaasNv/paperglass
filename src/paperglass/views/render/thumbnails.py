"""Page thumbnails for the report: what a person sees, small enough to carry in the JSON."""

from __future__ import annotations

import base64
import io

from PIL import Image

from paperglass.models import RenderCrop
from paperglass.models.raster import PageRaster

THUMBNAIL_WIDTH_PX = 720
THUMBNAIL_QUALITY = 72
THUMBNAIL_PAGE_CAP = 20
"""Pages beyond the cap carry no thumbnail; their runs are still classified."""


def thumbnail_data_uri(raster: PageRaster, width_px: int = THUMBNAIL_WIDTH_PX) -> RenderCrop:
    image = Image.open(io.BytesIO(raster.png)).convert("RGB")
    if image.width > width_px:
        ratio = width_px / image.width
        image = image.resize((width_px, max(1, round(image.height * ratio))), Image.Resampling.LANCZOS)
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=THUMBNAIL_QUALITY, optimize=True)
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return RenderCrop(data_uri=f"data:image/jpeg;base64,{encoded}")
