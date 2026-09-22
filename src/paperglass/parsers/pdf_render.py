"""Render PDF pages with pypdfium2. Runs inside the sandbox; returns PNG bytes per page."""

from __future__ import annotations

import io

from paperglass.models.raster import PageRaster


def render_pages(data: bytes, dpi: int, numbers: tuple[int, ...]) -> tuple[PageRaster, ...]:
    import pypdfium2 as pdfium  # noqa: PLC0415  # parsers import inside the sandboxed call

    document = pdfium.PdfDocument(data)
    rasters: list[PageRaster] = []
    try:
        for number in numbers:
            page = document[number - 1]
            width_pt, height_pt = page.get_size()
            bitmap = page.render(scale=dpi / 72, draw_annots=True, may_draw_forms=True)
            image = bitmap.to_pil().convert("RGB")
            buffer = io.BytesIO()
            image.save(buffer, format="PNG", optimize=False, compress_level=1)
            rasters.append(
                PageRaster(
                    number=number,
                    dpi=dpi,
                    width_px=image.width,
                    height_px=image.height,
                    width_pt=float(width_pt),
                    height_pt=float(height_pt),
                    png=buffer.getvalue(),
                )
            )
            page.close()
    finally:
        document.close()
    return tuple(rasters)
