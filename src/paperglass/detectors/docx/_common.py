"""Shared helpers for DOCX detectors."""

from __future__ import annotations

from paperglass.models.docx import DocxRun


def locate(run: DocxRun) -> str:
    return f"run {run.index} of paragraph {run.paragraph} in word/document.xml"


def reproduce(run: DocxRun) -> str:
    return f"paperglass show --part word/document.xml --paragraph {run.paragraph} --run {run.index} FILE"


def preview(text: str, limit: int = 80) -> str:
    text = text.replace("\n", " ")
    return text if len(text) <= limit else text[: limit - 3] + "..."
