"""Shared helpers for PDF detectors: the reproduce command and the page-object loop."""

from __future__ import annotations

from collections.abc import Callable, Iterable

from paperglass.detectors.base import Candidate, Detector
from paperglass.models import PdfTextObject
from paperglass.views.context import PageContext

PAINTING_MODES = frozenset({0, 2, 4, 6})
"""Text render modes that fill the glyphs (mode 1 and 5 stroke only; 3 and 7 paint nothing)."""


def reproduce(ctx: PageContext, obj: PdfTextObject) -> str:
    """The one-line command that shows the instruction behind a finding."""
    target = f"--page {ctx.page_number} --instruction {obj.instruction}"
    if ctx.structure is not None and ctx.structure.content_object is not None:
        target += f" --object {ctx.structure.content_object}"
    return f"paperglass show {target} FILE"


def preview(text: str, limit: int = 80) -> str:
    text = text.replace("\n", " ")
    return text if len(text) <= limit else text[: limit - 3] + "..."


class TextObjectDetector(Detector):
    """A detector that judges each text object on the page independently."""

    def check(self, ctx: PageContext, obj: PdfTextObject) -> Candidate | None:
        raise NotImplementedError

    def probe(self, ctx: PageContext) -> Iterable[Candidate]:
        if ctx.structure is None:
            return ()
        return [
            candidate
            for obj in ctx.structure.text_objects
            if obj.text.strip() and (candidate := self.check(ctx, obj)) is not None
        ]


def each_object(
    ctx: PageContext, judge: Callable[[PdfTextObject], Candidate | None]
) -> list[Candidate]:
    if ctx.structure is None:
        return []
    return [c for obj in ctx.structure.text_objects if obj.text.strip() and (c := judge(obj))]
