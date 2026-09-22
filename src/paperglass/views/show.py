"""`paperglass show` targets, run inside the sandbox: the bytes behind a finding."""

from __future__ import annotations

from collections.abc import Callable

from paperglass.ingest import Limits, run_sandboxed
from paperglass.models import ParseFailure
from paperglass.parsers import show as _show

TARGETS: dict[str, Callable[..., str]] = {
    "instruction": _show.pdf_instruction,
    "object": _show.pdf_object,
    "font": _show.pdf_font,
    "annotation": _show.pdf_annotation,
    "info": _show.pdf_info,
    "xmp": _show.pdf_xmp,
    "actions": _show.pdf_actions,
    "embedded": _show.pdf_embedded,
    "part": _show.docx_part,
    "text_run": _show.text_run,
}


def show(
    target: str, args: tuple[object, ...], *, limits: Limits
) -> tuple[str | None, ParseFailure | None]:
    result = run_sandboxed(TARGETS[target], args, limits=limits, parser="show")
    if result.failure is not None or result.value is None:
        failure = result.failure or ParseFailure(
            stage=0, parser="show", reason="crash", message="no output"
        )
        return None, failure
    return str(result.value), None
