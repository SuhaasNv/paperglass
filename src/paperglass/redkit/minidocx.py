"""A tiny, dependency-free DOCX writer for fixtures: the OOXML parts by hand, deterministic."""

from __future__ import annotations

import io
import zipfile
from dataclasses import dataclass, field

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

CONTENT_TYPES = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
    '<Default Extension="xml" ContentType="application/xml"/>'
    '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
    "{extra}"
    "</Types>"
)
ROOT_RELS = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
    "{extra}"
    "</Relationships>"
)
DOC_RELS = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    "{extra}"
    "</Relationships>"
)


def run(text: str, *, props: str = "") -> str:
    """One w:r. props is raw w:rPr content such as '<w:vanish/>' or '<w:color w:val="FFFFFF"/>'."""
    rpr = f"<w:rPr>{props}</w:rPr>" if props else ""
    return f'<w:r>{rpr}<w:t xml:space="preserve">{_escape(text)}</w:t></w:r>'


def paragraph(*runs: str) -> str:
    return "<w:p>" + "".join(runs) + "</w:p>"


def _escape(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


@dataclass(frozen=True)
class Docx:
    body: str
    """Raw paragraphs for w:body."""
    parts: dict[str, str] = field(default_factory=dict)
    """Extra parts by zip name (word/comments.xml, word/header1.xml, docProps/core.xml, ...)."""
    content_types: str = ""
    root_rels: str = ""
    doc_rels: str = ""


def _info(name: str) -> zipfile.ZipInfo:
    """A fixed timestamp so the same document always gives the same bytes."""
    return zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))


def build(doc: Docx) -> bytes:
    document = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:document xmlns:w="{W}" '
        'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing">'
        f"<w:body>{doc.body}</w:body></w:document>"
    )
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            _info("[Content_Types].xml"), CONTENT_TYPES.format(extra=doc.content_types)
        )
        archive.writestr(_info("_rels/.rels"), ROOT_RELS.format(extra=doc.root_rels))
        archive.writestr(_info("word/_rels/document.xml.rels"), DOC_RELS.format(extra=doc.doc_rels))
        archive.writestr(_info("word/document.xml"), document)
        for name, content in sorted(doc.parts.items()):
            archive.writestr(_info(name), content)
    return buffer.getvalue()


def simple(*paragraphs: str) -> bytes:
    return build(Docx(body="".join(paragraph(run(p)) for p in paragraphs)))
