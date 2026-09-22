"""A tiny, dependency-free PDF writer for fixtures and tests.

Produces a valid single-font PDF from a list of pages, each a content stream you write
by hand, so a fixture can set a render mode, a fill colour, a font size, a clip or an
optional content group exactly. Deterministic: same input, same bytes. The Red Kit
(v0.5.0) grows out of this.
"""

from __future__ import annotations

from dataclasses import dataclass, field

PAGE_WIDTH = 612
PAGE_HEIGHT = 792


@dataclass(frozen=True)
class Page:
    content: str
    width: int = PAGE_WIDTH
    height: int = PAGE_HEIGHT
    extra_resources: str = ""
    """Extra entries for the page's /Resources dictionary, for example ExtGState or OCG refs."""
    extra_objects: tuple[str, ...] = field(default_factory=tuple)
    """Whole extra objects this page needs, numbered after the fixed ones (see build)."""


def text(
    content: str,
    *,
    x: float = 72,
    y: float = 700,
    size: float = 12,
    font: str = "F1",
    render_mode: int | None = None,
    fill: str | None = None,
) -> str:
    """One text object. fill is a PDF colour operator string such as '1 1 1 rg'."""
    ops = ["BT", f"/{font} {size:g} Tf"]
    if render_mode is not None:
        ops.append(f"{render_mode} Tr")
    if fill is not None:
        ops.append(fill)
    ops.append(f"{x:g} {y:g} Td")
    ops.append(f"({_escape(content)}) Tj")
    ops.append("ET")
    return "\n".join(ops)


def _escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def build(pages: list[Page], *, catalog_extra: str = "", trailer_extra: str = "") -> bytes:
    """Assemble a PDF 1.7 file with Helvetica as /F1 and one content stream per page."""
    objects: list[bytes] = []

    def add(body: str | bytes) -> int:
        objects.append(body.encode("latin-1") if isinstance(body, str) else body)
        return len(objects)

    catalog = add("placeholder")
    pages_obj = add("placeholder")
    font = add("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
    page_ids: list[int] = []
    for page in pages:
        stream = page.content.encode("latin-1")
        content = add(
            b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream"
        )
        extra_ids = [add(obj) for obj in page.extra_objects]
        refs = [f"{i} 0 R" for i in extra_ids]
        resources = f"<< /Font << /F1 {font} 0 R >> {page.extra_resources.format(*refs)} >>"
        page_id = add(
            f"<< /Type /Page /Parent {pages_obj} 0 R /MediaBox [0 0 {page.width} {page.height}] "
            f"/Contents {content} 0 R /Resources {resources} >>"
        )
        page_ids.append(page_id)
    kids = " ".join(f"{i} 0 R" for i in page_ids)
    objects[pages_obj - 1] = f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode(
        "latin-1"
    )
    objects[catalog - 1] = f"<< /Type /Catalog /Pages {pages_obj} 0 R {catalog_extra} >>".encode(
        "latin-1"
    )

    out = bytearray(b"%PDF-1.7\n%\xe2\xe3\xcf\xd3\n")
    offsets: list[int] = []
    for number, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{number} 0 obj\n".encode() + body + b"\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode()
    out += b"0000000000 65535 f \n"
    for offset in offsets:
        out += f"{offset:010d} 00000 n \n".encode()
    out += (
        f"trailer\n<< /Size {len(objects) + 1} /Root {catalog} 0 R {trailer_extra} >>\n"
        f"startxref\n{xref}\n%%EOF\n"
    ).encode()
    return bytes(out)


def simple(content: str = "Hello Paperglass", **kwargs: float | str | int | None) -> bytes:
    """One page, one visible line."""
    return build([Page(text(content, **kwargs))])  # type: ignore[arg-type]  # kwargs mirror text()
