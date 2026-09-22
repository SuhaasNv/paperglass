"""View A for plain text and Markdown: one run per non-empty line, no positions."""

from __future__ import annotations

from paperglass.models import DocumentText, PageText, TextRun


def plain_extract(data: bytes) -> DocumentText:
    text = data.decode("utf-8", errors="replace")
    runs = tuple(
        TextRun(text=line, offset=index)
        for index, line in enumerate(text.splitlines())
        if line.strip()
    )
    return DocumentText(
        extractor="plain",
        extractor_version="1",
        pages=(PageText(number=1, width=612, height=792, runs=runs),),
    )
