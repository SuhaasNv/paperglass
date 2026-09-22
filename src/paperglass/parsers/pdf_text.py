"""Raw View A extraction per backend. Every function here runs inside the sandbox.

Each function takes the file bytes and returns a DocumentText. They are module-level so
the spawned child can import them by name, and they never catch exceptions: a crash is
the sandbox's business.
"""

from __future__ import annotations

import ctypes
import io
from importlib.metadata import version as _version

from paperglass.models import BBox, DocumentText, PageText, TextRun

_LINE_BREAKS = frozenset("\r\n")
_GAP_FACTOR = 0.6
"""A horizontal gap wider than this many em (font size) starts a new run."""


def pypdfium2_extract(data: bytes) -> DocumentText:
    import pypdfium2 as pdfium  # noqa: PLC0415  # parsers import inside the sandboxed call
    from pypdfium2 import raw  # noqa: PLC0415

    document = pdfium.PdfDocument(data)
    pages: list[PageText] = []
    try:
        for index in range(len(document)):
            page = document[index]
            width, height = page.get_size()
            textpage = page.get_textpage()
            try:
                runs = _pdfium_runs(textpage, raw)
            finally:
                textpage.close()
            page.close()
            pages.append(PageText(number=index + 1, width=width, height=height, runs=tuple(runs)))
    finally:
        document.close()
    return DocumentText(
        extractor="pypdfium2", extractor_version=_version("pypdfium2"), pages=tuple(pages)
    )


def _pdfium_runs(textpage: object, raw: object) -> list[TextRun]:
    """Group characters into runs: a run breaks at a line break, a font change or a wide gap."""
    count: int = textpage.count_chars()  # type: ignore[attr-defined]  # PdfTextPage
    runs: list[TextRun] = []
    chars: list[str] = []
    boxes: list[tuple[float, float, float, float]] = []
    font_name: str | None = None
    size: float | None = None
    start = 0

    def flush() -> None:
        nonlocal chars, boxes, start
        joined = "".join(chars).strip()
        if joined:
            x0 = min(b[0] for b in boxes)
            y0 = min(b[1] for b in boxes)
            x1 = max(b[2] for b in boxes)
            y1 = max(b[3] for b in boxes)
            runs.append(
                TextRun(
                    text=joined,
                    bbox=BBox(x0=x0, y0=y0, x1=x1, y1=y1),
                    font=font_name,
                    size_pt=size,
                    offset=start,
                )
            )
        chars = []
        boxes = []

    for index in range(count):
        char = textpage.get_text_range(index, 1)  # type: ignore[attr-defined]
        if char in _LINE_BREAKS or char == "":
            flush()
            start = index + 1
            continue
        this_font = _pdfium_font(textpage, raw, index)
        this_size = _pdfium_size(textpage, raw, index)
        box = textpage.get_charbox(index, loose=False)  # type: ignore[attr-defined]
        if boxes and (
            this_font != font_name
            or (size is not None and box[0] - boxes[-1][2] > _GAP_FACTOR * max(size, 1.0))
        ):
            flush()
            start = index
        if not boxes:
            font_name, size = this_font, this_size
        chars.append(char)
        boxes.append((float(box[0]), float(box[1]), float(box[2]), float(box[3])))
    flush()
    return runs


def _pdfium_font(textpage: object, raw: object, index: int) -> str | None:
    buffer = ctypes.create_string_buffer(256)
    flags = ctypes.c_int()
    length = raw.FPDFText_GetFontInfo(textpage, index, buffer, 256, ctypes.byref(flags))  # type: ignore[attr-defined]
    if not length:
        return None
    return buffer.value.decode("utf-8", errors="replace") or None


def _pdfium_size(textpage: object, raw: object, index: int) -> float | None:
    size = float(raw.FPDFText_GetFontSize(textpage, index))  # type: ignore[attr-defined]
    return size if size > 0 else None


def pdfplumber_extract(data: bytes) -> DocumentText:
    import pdfplumber  # noqa: PLC0415

    pages: list[PageText] = []
    with pdfplumber.open(io.BytesIO(data)) as document:
        for index, page in enumerate(document.pages):
            height = float(page.height)
            runs = [
                TextRun(
                    text=str(word["text"]),
                    bbox=BBox(
                        x0=float(word["x0"]),
                        y0=height - float(word["bottom"]),
                        x1=float(word["x1"]),
                        y1=height - float(word["top"]),
                    ),
                    font=str(word.get("fontname")) if word.get("fontname") else None,
                    size_pt=float(word["size"]) if word.get("size") else None,
                    offset=position,
                )
                for position, word in enumerate(
                    page.extract_words(extra_attrs=["fontname", "size"], keep_blank_chars=False)
                )
            ]
            pages.append(
                PageText(number=index + 1, width=float(page.width), height=height, runs=tuple(runs))
            )
    return DocumentText(
        extractor="pdfplumber", extractor_version=_version("pdfplumber"), pages=tuple(pages)
    )


def pypdf_extract(data: bytes) -> DocumentText:
    """pypdf gives text and a text matrix per fragment, no glyph widths: the bbox is a point."""
    import pypdf  # noqa: PLC0415

    reader = pypdf.PdfReader(io.BytesIO(data))
    pages: list[PageText] = []
    for index, page in enumerate(reader.pages):
        box = page.mediabox
        width, height = float(box.width), float(box.height)
        runs: list[TextRun] = []

        def visitor(
            text: str,
            cm: list[float],
            tm: list[float],
            font_dict: dict[str, object] | None,
            font_size: float,
            _runs: list[TextRun] = runs,
        ) -> None:
            stripped = text.strip()
            if not stripped:
                return
            x, y = float(tm[4]) + float(cm[4]), float(tm[5]) + float(cm[5])
            font = None
            if font_dict is not None and "/BaseFont" in font_dict:
                font = str(font_dict["/BaseFont"]).lstrip("/")
            _runs.append(
                TextRun(
                    text=stripped,
                    bbox=BBox(x0=x, y0=y, x1=x, y1=y + float(font_size or 0)),
                    font=font,
                    size_pt=float(font_size) if font_size else None,
                    offset=len(_runs),
                )
            )

        page.extract_text(visitor_text=visitor)
        pages.append(PageText(number=index + 1, width=width, height=height, runs=tuple(runs)))
    return DocumentText(extractor="pypdf", extractor_version=_version("pypdf"), pages=tuple(pages))


def pdfminer_extract(data: bytes) -> DocumentText:
    from pdfminer.high_level import extract_pages  # noqa: PLC0415
    from pdfminer.layout import LTChar, LTTextContainer, LTTextLine  # noqa: PLC0415

    pages: list[PageText] = []
    for index, layout in enumerate(extract_pages(io.BytesIO(data))):
        runs: list[TextRun] = []
        for element in layout:
            if not isinstance(element, LTTextContainer):
                continue
            for line in element:
                if not isinstance(line, LTTextLine):
                    continue
                stripped = line.get_text().strip()
                if not stripped:
                    continue
                chars = [c for c in line if isinstance(c, LTChar)]
                font = chars[0].fontname if chars else None
                size = float(chars[0].size) if chars else None
                runs.append(
                    TextRun(
                        text=stripped,
                        bbox=BBox(x0=line.x0, y0=line.y0, x1=line.x1, y1=line.y1),
                        font=font,
                        size_pt=size,
                        offset=len(runs),
                    )
                )
        pages.append(
            PageText(
                number=index + 1,
                width=float(layout.width),
                height=float(layout.height),
                runs=tuple(runs),
            )
        )
    return DocumentText(
        extractor="pdfminer.six", extractor_version=_version("pdfminer.six"), pages=tuple(pages)
    )
