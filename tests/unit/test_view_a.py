"""View A: every backend returns the visible text with a position, through the sandbox."""

from __future__ import annotations

import pytest

from paperglass.ingest import Limits
from paperglass.ingest.sniff import InputType
from paperglass.views.extract import DEFAULT_EXTRACTOR, EXTRACTORS, available, get
from tests.helpers.minipdf import Page, build, simple, text

LIMITS = Limits(wall_seconds=20.0, cpu_seconds=20)


@pytest.mark.parametrize("name", list(EXTRACTORS))
def test_every_backend_reads_the_visible_line(name: str) -> None:
    outcome = get(name).extract(simple("Hello Paperglass"), limits=LIMITS)
    assert outcome.ok, outcome.failure
    document = outcome.document
    assert document is not None
    assert document.extractor == name
    assert document.page_count == 1
    assert "Hello" in document.text and "Paperglass" in document.text
    page = document.pages[0]
    assert page.width == 612 and page.height == 792
    first = page.runs[0]
    assert first.bbox is not None
    assert 60 < first.bbox.x0 < 90
    assert 690 < first.bbox.y0 < 712


@pytest.mark.parametrize("name", ["pypdfium2", "pdfplumber", "pdfminer.six"])
def test_font_and_size_are_reported(name: str) -> None:
    document = get(name).extract(simple("Sized", size=9), limits=LIMITS).document
    assert document is not None
    run = document.pages[0].runs[0]
    assert run.size_pt is not None and 8.5 <= run.size_pt <= 9.5
    assert run.font is not None and "Helvetica" in run.font


def test_default_backend_splits_runs_at_line_breaks_and_gaps() -> None:
    content = text("Left") + "\n" + text("Right", x=400) + "\n" + text("Below", y=650)
    document = get(DEFAULT_EXTRACTOR).extract(build([Page(content)]), limits=LIMITS).document
    assert document is not None
    texts = [run.text for run in document.pages[0].runs]
    assert texts == ["Left", "Right", "Below"]


def test_two_pages() -> None:
    data = build([Page(text("One")), Page(text("Two"))])
    document = get(DEFAULT_EXTRACTOR).extract(data, limits=LIMITS).document
    assert document is not None
    assert [p.number for p in document.pages] == [1, 2]
    assert document.pages[1].runs[0].text == "Two"


def test_garbage_is_a_parse_failure_not_an_exception() -> None:
    outcome = get(DEFAULT_EXTRACTOR).extract(b"%PDF-1.7\ngarbage", limits=LIMITS)
    assert not outcome.ok
    assert outcome.failure is not None
    assert outcome.failure.parser == "pypdfium2"
    assert outcome.failure.reason == "crash"


def test_available_lists_default_first_and_filters_by_type() -> None:
    names = [e.name for e in available(InputType.PDF)]
    assert names[0] == DEFAULT_EXTRACTOR
    assert set(names) == set(EXTRACTORS)
    assert available(InputType.DOCX) == []


def test_unknown_extractor() -> None:
    with pytest.raises(KeyError, match="unknown extractor"):
        get("nope")
