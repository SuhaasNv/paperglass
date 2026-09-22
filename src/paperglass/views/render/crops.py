"""Evidence crops as PNG data URIs, padded so a person sees the context."""

from __future__ import annotations

import base64
import io

from PIL import Image

from paperglass.models import BBox, RenderCrop
from paperglass.models.raster import PageRaster
from paperglass.views.render.ink import to_pixels

CROP_PAD_PT = 6.0
MAX_CROP_PX = 1200


def crop_image(raster: PageRaster, bbox: BBox, pad_pt: float = CROP_PAD_PT) -> Image.Image:
    x0, y0, x1, y1 = to_pixels(raster, bbox, pad_pt=pad_pt)
    image = Image.open(io.BytesIO(raster.png)).convert("RGB")
    crop = image.crop((x0, y0, max(x1, x0 + 1), max(y1, y0 + 1)))
    if crop.width > MAX_CROP_PX:
        ratio = MAX_CROP_PX / crop.width
        crop = crop.resize((MAX_CROP_PX, max(1, int(crop.height * ratio))))
    return crop


def crop_data_uri(raster: PageRaster, bbox: BBox) -> RenderCrop:
    crop = crop_image(raster, bbox)
    buffer = io.BytesIO()
    crop.save(buffer, format="PNG", optimize=True)
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return RenderCrop(data_uri=f"data:image/png;base64,{encoded}")
