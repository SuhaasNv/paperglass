"""DOCX View A and View C."""

from __future__ import annotations

from paperglass.ingest import Limits
from paperglass.redkit import minidocx
from paperglass.views.extract import get
from paperglass.views.pages import build_pages
from paperglass.views.structure import docx_structure

LIMITS = Limits(wall_seconds=60.0, cpu_seconds=60)


def test_view_a_reads_paragraphs() -> None:
    document = get("python-docx").extract(minidocx.simple("One", "Two"), limits=LIMITS).document
    assert document is not None
    assert [r.text for r in document.pages[0].runs] == ["One", "Two"]


def test_view_c_records_run_properties_and_parts() -> None:
    body = (
        minidocx.paragraph(
            minidocx.run("plain"),
            minidocx.run("gone", props="<w:vanish/>"),
            minidocx.run("white", props='<w:color w:val="FFFFFF"/><w:sz w:val="2"/>'),
        )
        + "<w:p><w:del><w:r><w:delText>removed</w:delText></w:r></w:del></w:p>"
    )
    body += minidocx.paragraph(
        '<w:r><w:instrText xml:space="preserve"> QUOTE "hidden field" </w:instrText></w:r>'
    )
    doc = minidocx.build(
        minidocx.Docx(
            body=body,
            parts={
                "word/header1.xml": (
                    f'<w:hdr xmlns:w="{minidocx.W}">'
                    "<w:p><w:r><w:t>Header text</w:t></w:r></w:p></w:hdr>"
                )
            },
        )
    )
    outcome = docx_structure(doc, limits=LIMITS)
    assert outcome.failure is None, outcome.failure
    structure = outcome.structure
    assert structure is not None
    texts = {r.text: r for r in structure.runs}
    assert texts["gone"].vanish and not texts["plain"].vanish
    assert texts["white"].color == "FFFFFF" and texts["white"].grey == 1.0
    assert texts["white"].size_pt == 1.0
    field = next(r for r in structure.runs if r.field_code)
    assert "hidden field" in field.text
    header = next(p for p in structure.parts if p.kind == "header")
    assert header.text == "Header text"
    assert not structure.has_macros


def test_build_pages_attaches_docx_structure() -> None:
    stage0 = build_pages(minidocx.simple("Hello"), limits=LIMITS)
    assert stage0.input_type.value == "docx"
    assert stage0.extractor == "python-docx"
    assert stage0.pages[0].docx is not None
    assert stage0.pages[0].runs[0].text == "Hello"
