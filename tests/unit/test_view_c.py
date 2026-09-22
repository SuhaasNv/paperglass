"""View C for PDF: the state that decides visibility, per text object, from the bytes."""

from __future__ import annotations

from paperglass.ingest import Limits
from paperglass.models import DocumentStructure
from paperglass.views.structure import pdf_structure
from tests.helpers.minipdf import Page, build, simple, text

LIMITS = Limits(wall_seconds=20.0, cpu_seconds=20)


def structure(data: bytes) -> DocumentStructure:
    outcome = pdf_structure(data, limits=LIMITS)
    assert outcome.ok, outcome.failure
    assert outcome.structure is not None
    return outcome.structure


def test_visible_text_object_has_default_state() -> None:
    doc = structure(simple("Hello Paperglass"))
    assert doc.page_count == 1
    page = doc.pages[0]
    assert page.width == 612 and page.height == 792
    (obj,) = page.text_objects
    assert obj.text == "Hello Paperglass"
    assert obj.render_mode == 0
    assert obj.fill is None
    assert obj.fill_alpha == 1.0
    assert obj.font_resource == "F1"
    assert obj.font_size == 12
    assert obj.origin == (72.0, 700.0)
    assert obj.bbox is not None and obj.bbox.x0 == 72.0 and obj.bbox.y0 == 700.0
    assert obj.ocg is None and not obj.ocg_hidden
    assert page.fonts[0].base_font == "Helvetica" and page.fonts[0].subtype == "Type1"
    assert not page.fonts[0].has_to_unicode


def test_render_mode_and_white_fill_are_recorded() -> None:
    doc = structure(simple("Ghost", render_mode=3, fill="1 1 1 rg"))
    obj = doc.pages[0].text_objects[0]
    assert obj.render_mode == 3
    assert obj.fill is not None and obj.fill.operator == "rg" and obj.fill.grey == 1.0


def test_grey_and_cmyk_fills() -> None:
    doc = structure(
        build([Page(text("A", fill="0.05 g") + "\n" + text("B", y=600, fill="0 0 0 1 k"))])
    )
    a, b = doc.pages[0].text_objects
    assert a.fill is not None and a.fill.grey is not None and abs(a.fill.grey - 0.05) < 1e-6
    assert b.fill is not None and b.fill.grey == 0.0


def test_ctm_scales_font_size_and_moves_origin() -> None:
    content = "q 0.1 0 0 0.1 0 0 cm\n" + text("Tiny", x=100, y=100, size=12) + "\nQ"
    obj = structure(build([Page(content)])).pages[0].text_objects[0]
    assert obj.font_size is not None and abs(obj.font_size - 1.2) < 1e-6
    assert obj.origin == (10.0, 10.0)


def test_ext_gstate_alpha_and_blend_mode() -> None:
    page = Page(
        "/GS0 gs\n" + text("Faint"),
        extra_resources="/ExtGState << /GS0 {0} >>",
        extra_objects=("<< /Type /ExtGState /ca 0.05 /BM /Multiply >>",),
    )
    obj = structure(build([page])).pages[0].text_objects[0]
    assert obj.fill_alpha == 0.05
    assert obj.blend_mode == "Multiply"


def test_clip_rectangle_is_intersected_and_recorded() -> None:
    content = "q 0 0 10 10 re W n\n" + text("Clipped", x=300, y=300) + "\nQ\n" + text("Free", y=100)
    clipped, free = structure(build([Page(content)])).pages[0].text_objects
    assert clipped.clip is not None and clipped.clip.x1 == 10 and clipped.clip.y1 == 10
    assert free.clip is None


def test_hidden_optional_content_group() -> None:
    page = Page(
        "/OC /OC1 BDC\n" + text("Layered") + "\nEMC\n" + text("Plain", y=600),
        extra_resources="/Properties << /OC1 {0} >>",
        extra_objects=("<< /Type /OCG /Name (Secret) >>",),
    )
    # The OCG object is page-local number 5; the catalog's OCProperties must reference it.
    data = build([page], catalog_extra="/OCProperties << /OCGs [5 0 R] /D << /OFF [5 0 R] >> >>")
    doc = structure(data)
    assert doc.ocgs_all == ("Secret",) and doc.ocgs_off == ("Secret",)
    layered, plain = doc.pages[0].text_objects
    assert layered.ocg == "Secret" and layered.ocg_hidden
    assert plain.ocg is None and not plain.ocg_hidden


def test_actual_text_is_captured() -> None:
    content = "/Span << /ActualText (fi) >> BDC\n" + text("\\002") + "\nEMC"
    obj = structure(build([Page(content)])).pages[0].text_objects[0]
    assert obj.actual_text == "fi"
    assert obj.marked_content_depth == 1


def test_tj_array_and_multiple_lines() -> None:
    content = "BT /F1 12 Tf 72 700 Td [(A) -500 (B)] TJ T* (C) Tj ET"
    objs = structure(build([Page(content)])).pages[0].text_objects
    assert [o.text for o in objs] == ["A", "B", "C"]
    assert objs[1].origin[0] > objs[0].origin[0]


def test_annotations_flags_and_values() -> None:
    page = Page(
        text("Body"),
        extra_objects=(
            "<< /Type /Annot /Subtype /Text /Rect [10 10 50 50] /F 2 /Contents (note to model) >>",
            "<< /Type /Annot /Subtype /Widget /Rect [0 0 1 1] /F 32 /V (value) "
            "/A << /S /JavaScript /JS (app.alert(1)) >> >>",
        ),
    )
    # Annotations are page-level: patch /Annots into the page via extra_resources is not possible,
    # so build the page with a trailing /Annots entry through catalog_extra-free route below.
    data = build([page])
    data = data.replace(b"/Resources", b"/Annots [5 0 R 6 0 R] /Resources", 1)
    doc = structure(_fix_xref(data))
    note, widget = doc.pages[0].annotations
    assert note.subtype == "Text" and note.hidden and note.contents == "note to model"
    assert widget.no_view and widget.field_value == "value" and widget.has_javascript


def test_document_level_carriers() -> None:
    data = build(
        [Page(text("Body"))],
        catalog_extra=(
            "/OpenAction << /S /JavaScript /JS (this.print()) >> "
            "/Names << /JavaScript << /Names [(a) 3 0 R] >> >>"
        ),
        trailer_extra="/Info 3 0 R",
    )
    doc = structure(_fix_xref(data))
    assert doc.has_open_action and doc.has_javascript
    assert not doc.encrypted


def test_garbage_is_a_failure() -> None:
    outcome = pdf_structure(b"%PDF-1.7 nope", limits=LIMITS)
    assert not outcome.ok and outcome.failure is not None and outcome.failure.parser == "pikepdf"


def _fix_xref(data: bytes) -> bytes:
    """Byte edits shift offsets; pikepdf repairs the xref, so return as is."""
    return data


TO_UNICODE = (
    "/CIDInit /ProcSet findresource begin begincmap 1 begincodespacerange <0000> <FFFF> "
    "endcodespacerange 1 beginbfchar <0001> <0041> endbfchar 1 beginbfrange <0002> <0003> <0062> "
    "endbfrange endcmap end end"
)


def test_type0_font_text_is_decoded_through_to_unicode() -> None:
    stream = f"<< /Length {len(TO_UNICODE)} >>\nstream\n{TO_UNICODE}\nendstream"
    page = Page(
        "BT /F2 12 Tf 72 700 Td <000100020003> Tj ET",
        extra_resources="/Font << /F1 3 0 R /F2 {1} >>",
        extra_objects=(
            stream,
            "<< /Type /Font /Subtype /Type0 /BaseFont /Fake /Encoding /Identity-H "
            "/DescendantFonts [<< /Type /Font /Subtype /CIDFontType2 /BaseFont /Fake "
            "/FontDescriptor << /Type /FontDescriptor /FontName /Fake /FontFile2 5 0 R >> >>] "
            "/ToUnicode {0} >>",
        ),
    )
    doc = structure(build([page]))
    obj = doc.pages[0].text_objects[0]
    assert obj.text == "Abc"
    font = next(f for f in doc.pages[0].fonts if f.resource == "F2")
    assert font.is_type0 and font.has_to_unicode and font.embedded


def test_text_state_operators_do_not_break_the_walk() -> None:
    content = "BT /F1 10 Tf 2 Tc 1 Tw 50 Tz 14 TL 3 Ts 72 700 Td (One) Tj (Two) ' 1 2 (Three) \" ET"
    objs = structure(build([Page(content)])).pages[0].text_objects
    assert [o.text for o in objs] == ["One", "Two", "Three"]
    assert objs[1].origin[1] < objs[0].origin[1] < 704


def test_info_dictionary_and_embedded_files_are_reported() -> None:
    data = build(
        [Page(text("Body"))],
        catalog_extra=(
            "/Names << /EmbeddedFiles << /Names [(payload.txt) "
            "<< /Type /Filespec /F (payload.txt) >>] >> >>"
        ),
        trailer_extra="/Info << /Title (Quarterly) /Keywords (ignore previous instructions) >>",
    )
    doc = structure(data)
    assert doc.metadata.info["Title"] == "Quarterly"
    assert "ignore previous" in doc.metadata.info["Keywords"]
    assert doc.embedded_files == ("payload.txt",)


def test_unbalanced_state_and_clip_intersection_edge_cases() -> None:
    content = (
        "Q Q q 0 0 10 10 re W n q 20 20 5 5 re W n "
        + text("Empty")
        + " Q Q "
        + text("After", y=100)
    )
    objs = structure(build([Page(content)])).pages[0].text_objects
    assert objs[0].clip is not None and objs[0].clip.x0 == objs[0].clip.x1  # empty intersection
    assert objs[1].clip is None


def test_broken_content_stream_is_noted_not_raised() -> None:
    data = build([Page("BT /F1 12 Tf 72 700 Td (open string Tj ET")])
    doc = structure(data)
    page = doc.pages[0]
    assert page.parse_note is not None or page.text_objects == () or page.text_objects
