"""View B: render once, check ink per region without OCR, OCR only the crops."""

from __future__ import annotations

import pytest

from paperglass.ingest import Limits
from paperglass.models import BBox, PageRaster
from paperglass.redkit.minipdf import Page, build, simple, text
from paperglass.views.pages import build_pages
from paperglass.views.render import (
    agreement,
    choose_dpi,
    crop_data_uri,
    ink_check,
    ocr_available,
    ocr_crop,
    render_document,
    to_pixels,
)

LIMITS = Limits(wall_seconds=60.0, cpu_seconds=60)


def raster_of(data: bytes, dpi: int = 150) -> PageRaster:
    outcome = render_document(data, limits=LIMITS, numbers=(1,), dpi=dpi)
    assert outcome.failure is None, outcome.failure
    return outcome.rasters[0]


def test_render_produces_a_png_at_the_requested_dpi() -> None:
    raster = raster_of(simple("Hello"), dpi=150)
    assert raster.width_px == 1275 and raster.height_px == 1651
    assert raster.png.startswith(b"\x89PNG")
    assert raster.width_pt == 612 and raster.height_pt == 792


def test_choose_dpi_rises_for_small_fonts() -> None:
    normal = build_pages(simple("Normal"), limits=LIMITS).structure
    small = build_pages(simple("Small", size=4), limits=LIMITS).structure
    assert choose_dpi(normal) == 150
    assert choose_dpi(small) == 200
    assert choose_dpi(None) == 150


def test_to_pixels_flips_the_y_axis() -> None:
    raster = raster_of(simple("Hello"))
    x0, y0, x1, y1 = to_pixels(raster, BBox(x0=72, y0=700, x1=172, y1=712))
    assert x0 == 150 and x1 == 359
    assert y0 == int((792 - 712) * 150 / 72) and y1 <= int((792 - 700) * 150 / 72) + 1


def test_visible_black_text_has_ink() -> None:
    raster = raster_of(simple("Hello Paperglass"))
    result = ink_check(raster, BBox(x0=72, y0=698, x1=180, y1=712))
    assert result.classification == "visible"
    assert result.ink_fraction > 0.015 and result.contrast > 0.5
    assert result.background > 0.95


def test_white_text_has_no_ink() -> None:
    raster = raster_of(simple("Hidden line", fill="1 1 1 rg"))
    result = ink_check(raster, BBox(x0=72, y0=698, x1=150, y1=712))
    assert result.classification == "invisible"
    assert result.ink_fraction < 0.002


def test_render_mode_three_has_no_ink_but_a_clip_mode_seven_neither() -> None:
    for mode in (3, 7):
        raster = raster_of(simple("Ghost text", render_mode=mode))
        assert ink_check(raster, BBox(x0=72, y0=698, x1=150, y1=712)).classification == "invisible"


def test_near_white_grey_text_is_invisible_or_uncertain() -> None:
    raster = raster_of(simple("Faint", fill="0.95 g"))
    result = ink_check(raster, BBox(x0=72, y0=698, x1=110, y1=712))
    assert result.classification in {"invisible", "uncertain"}


def test_empty_region_is_invisible() -> None:
    raster = raster_of(simple("Hello"))
    assert ink_check(raster, BBox(x0=300, y0=300, x1=300.1, y1=300.1)).classification == "invisible"


def test_crop_is_a_png_data_uri() -> None:
    raster = raster_of(simple("Hello"))
    crop = crop_data_uri(raster, BBox(x0=72, y0=698, x1=150, y1=712))
    assert crop.data_uri is not None and crop.data_uri.startswith("data:image/png;base64,")


@pytest.mark.ocr
@pytest.mark.skipif(not ocr_available(), reason="paperglass[ocr] not installed")
def test_ocr_reads_a_visible_crop_and_agreement_scores_it() -> None:
    raster = raster_of(simple("Hello Paperglass", size=14))
    read = ocr_crop(raster, BBox(x0=60, y0=690, x1=260, y1=720))
    assert "Hello" in read.text
    assert agreement("Hello Paperglass", read.text) > 0.8
    assert agreement("Hello Paperglass", "") == 0.0
    assert agreement("", "anything") == 1.0


@pytest.mark.ocr
@pytest.mark.skipif(not ocr_available(), reason="paperglass[ocr] not installed")
def test_ocr_on_white_text_reads_nothing() -> None:
    raster = raster_of(simple("Hidden line", fill="1 1 1 rg", size=14))
    read = ocr_crop(raster, BBox(x0=60, y0=690, x1=260, y1=720))
    assert read.text.strip() == ""


def test_two_page_render_numbers_pages() -> None:
    data = build([Page(text("One")), Page(text("Two"))])
    outcome = render_document(data, limits=LIMITS, numbers=(1, 2), dpi=72)
    assert [r.number for r in outcome.rasters] == [1, 2]
    assert outcome.rasters[0].width_px == 612
