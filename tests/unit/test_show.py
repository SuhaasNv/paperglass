"""The show targets, through the sandbox."""

from __future__ import annotations

import pathlib

from paperglass.ingest import Limits
from paperglass.redkit import minidocx
from paperglass.redkit.minipdf import Page, build, simple, text
from paperglass.views.show import show

ROOT = pathlib.Path(__file__).resolve().parents[2]
LIMITS = Limits(wall_seconds=60.0, cpu_seconds=60)


def test_pdf_targets() -> None:
    data = build(
        [Page(text("Body"))],
        catalog_extra=(
            "/Names << /EmbeddedFiles << /Names [(a.txt) << /Type /Filespec /F (a.txt) >>] >> >>"
        ),
        trailer_extra="/Info << /Title (T) >>",
    )
    assert "embedded files" in (show("embedded", (data,), limits=LIMITS)[0] or "")
    assert "Title" in (show("info", (data,), limits=LIMITS)[0] or "")
    assert "XMP" in (show("xmp", (data,), limits=LIMITS)[0] or "")
    assert "/Names" in (show("actions", (data,), limits=LIMITS)[0] or "")
    assert "none" in (show("actions", (simple("x"),), limits=LIMITS)[0] or "")
    assert "no font" in (show("font", (data, 1, "F9"), limits=LIMITS)[0] or "")
    assert "annotations" in (show("annotation", (data, 1, 3), limits=LIMITS)[0] or "")
    stream = show("object", (data, 4), limits=LIMITS)[0] or ""
    assert "stream" in stream
    assert "no embedded" in (show("embedded", (simple("x"),), limits=LIMITS)[0] or "")


def test_docx_and_text_targets() -> None:
    doc = minidocx.simple("One", "Two")
    assert "first 6000" in (
        show("part", (doc, "word/document.xml", None, None), limits=LIMITS)[0] or ""
    )
    assert "no part" in (show("part", (doc, "nope.xml", None, None), limits=LIMITS)[0] or "")
    assert "paragraphs" in (
        show("part", (doc, "word/document.xml", 9, None), limits=LIMITS)[0] or ""
    )
    assert "Two" in (show("part", (doc, "word/document.xml", 1, 0), limits=LIMITS)[0] or "")
    assert "non-empty lines" in (show("text_run", (b"a\n", 5), limits=LIMITS)[0] or "")


def test_failure_is_returned_not_raised() -> None:
    text_, failure = show("object", (b"%PDF-1.7 nope", 1), limits=LIMITS)
    assert text_ is None and failure is not None and failure.reason == "crash"
