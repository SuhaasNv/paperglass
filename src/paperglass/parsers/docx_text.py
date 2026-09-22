"""DOCX View A (python-docx paragraphs and runs) and View C (raw OOXML via lxml).

Both run inside the sandbox. Nothing is executed; a vbaProject part is noted, never read.
"""

from __future__ import annotations

import io
import re
import zipfile
from importlib.metadata import version as _version

from paperglass.models import DocumentText, PageText, TextRun
from paperglass.models.docx import DocxPart, DocxRun, DocxStructure

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
WP = "{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}"
CP = "{http://schemas.openxmlformats.org/package/2006/metadata/core-properties}"
DC = "{http://purl.org/dc/elements/1.1/}"


def docx_extract(data: bytes) -> DocumentText:
    import docx  # noqa: PLC0415  # parsers import inside the sandboxed call

    document = docx.Document(io.BytesIO(data))
    runs: list[TextRun] = []
    for index, paragraph in enumerate(document.paragraphs):
        text = paragraph.text
        if text.strip():
            runs.append(TextRun(text=text, offset=index))
    return DocumentText(
        extractor="python-docx",
        extractor_version=_version("python-docx"),
        pages=(PageText(number=1, width=612, height=792, runs=tuple(runs)),),
    )


def docx_structure(data: bytes) -> DocxStructure:
    from lxml import etree  # noqa: PLC0415

    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        names = set(archive.namelist())
        root = etree.fromstring(archive.read("word/document.xml"))
        parts: list[DocxPart] = []
        for name in sorted(names):
            parts.extend(_part(archive, name, etree))
        has_macros = any(n.lower().endswith("vbaproject.bin") for n in names)
    background = None
    bg = root.find(f"{W}background")
    if bg is not None:
        background = bg.get(f"{W}color")
    runs = list(_runs(root))
    parts.extend(_alt_texts(root))
    return DocxStructure(
        parser_version=_version("lxml"),
        runs=tuple(runs),
        parts=tuple(parts),
        page_background=background,
        has_macros=has_macros,
    )


def _grey(hex_colour: str | None) -> float | None:
    if not hex_colour or hex_colour.lower() == "auto" or len(hex_colour) != 6:
        return None
    try:
        r, g, b = (int(hex_colour[i : i + 2], 16) / 255.0 for i in (0, 2, 4))
    except ValueError:
        return None
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _runs(root: object) -> list[DocxRun]:
    out: list[DocxRun] = []
    body = root.find(f"{W}body")  # type: ignore[attr-defined]
    if body is None:
        return out
    for p_index, paragraph in enumerate(body.iter(f"{W}p")):
        r_index = 0
        for element in paragraph.iter():
            if element.tag not in (f"{W}r",):
                continue
            texts = [t.text or "" for t in element.iter(f"{W}t")]
            instr = [t.text or "" for t in element.iter(f"{W}instrText")]
            text = "".join(texts) or "".join(instr)
            if not text:
                continue
            rpr = element.find(f"{W}rPr")
            color = size = highlight = shading = None
            vanish = spec = False
            if rpr is not None:
                vanish = rpr.find(f"{W}vanish") is not None
                spec = rpr.find(f"{W}specVanish") is not None
                c = rpr.find(f"{W}color")
                color = c.get(f"{W}val") if c is not None else None
                sz = rpr.find(f"{W}sz")
                size = int(sz.get(f"{W}val", "0")) / 2 if sz is not None else None
                h = rpr.find(f"{W}highlight")
                highlight = h.get(f"{W}val") if h is not None else None
                shd = rpr.find(f"{W}shd")
                shading = shd.get(f"{W}fill") if shd is not None else None
            ancestors = {a.tag for a in element.iterancestors()}
            out.append(
                DocxRun(
                    paragraph=p_index,
                    index=r_index,
                    text=text,
                    vanish=vanish,
                    spec_vanish=spec,
                    color=color,
                    grey=_grey(color),
                    size_pt=size,
                    highlight=highlight,
                    shading_fill=shading,
                    deleted=f"{W}del" in ancestors,
                    inserted=f"{W}ins" in ancestors,
                    field_code=bool(instr) and not texts,
                )
            )
            r_index += 1
    return out


def _alt_texts(root: object) -> list[DocxPart]:
    out: list[DocxPart] = []
    for doc_pr in root.iter(f"{WP}docPr"):  # type: ignore[attr-defined]
        for key in ("descr", "title"):
            value = doc_pr.get(key)
            if value:
                out.append(DocxPart(kind="alt_text", name=f"docPr/{key}", text=value))
    return out


_TEXT_PARTS = {
    "word/comments.xml": "comment",
    "word/footnotes.xml": "footnote",
    "word/endnotes.xml": "endnote",
}


def _part(archive: zipfile.ZipFile, name: str, etree: object) -> list[DocxPart]:
    kind: str | None = _TEXT_PARTS.get(name)
    if name.startswith("word/header") and name.endswith(".xml"):
        kind = "header"
    elif name.startswith("word/footer") and name.endswith(".xml"):
        kind = "footer"
    if kind is not None:
        root = etree.fromstring(archive.read(name))  # type: ignore[attr-defined]
        text = " ".join(t.text or "" for t in root.iter(f"{W}t")).strip()
        return [DocxPart(kind=kind, name=name, text=text)] if text else []  # type: ignore[arg-type]
    if name == "docProps/core.xml":
        root = etree.fromstring(archive.read(name))  # type: ignore[attr-defined]
        out: list[DocxPart] = []
        for child in root:
            tag = re.sub(r"^\{.*\}", "", str(child.tag))
            if child.text and child.text.strip():
                out.append(DocxPart(kind="property", name=tag, text=child.text.strip()))
        return out
    return []
