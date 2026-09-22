"""Type from magic bytes, never from the extension. Zip guards for the OOXML family."""

from __future__ import annotations

import io
import zipfile
from enum import StrEnum
from typing import Final

from paperglass.ingest.limits import Limits
from paperglass.models import ParseFailure


class InputType(StrEnum):
    PDF = "pdf"
    DOCX = "docx"
    PPTX = "pptx"
    XLSX = "xlsx"
    PNG = "png"
    JPG = "jpg"
    TIFF = "tiff"
    HTML = "html"
    MARKDOWN = "md"
    TEXT = "txt"
    ZIP = "zip"
    UNKNOWN = "unknown"


_PDF: Final = b"%PDF-"
_PNG: Final = b"\x89PNG\r\n\x1a\n"
_JPG: Final = b"\xff\xd8\xff"
_TIFF_LE: Final = b"II*\x00"
_TIFF_BE: Final = b"MM\x00*"
_ZIP: Final = (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08")
_HTML_MARKERS: Final = (b"<!doctype html", b"<html", b"<head", b"<body")
_MD_MARKERS: Final = (b"# ", b"## ", b"- ", b"* ", b"```", b"[", b"1. ")


_MAGIC: Final[tuple[tuple[bytes, InputType], ...]] = (
    (_PDF, InputType.PDF),
    (_PNG, InputType.PNG),
    (_JPG, InputType.JPG),
    (_TIFF_LE, InputType.TIFF),
    (_TIFF_BE, InputType.TIFF),
)


def sniff(data: bytes) -> InputType:
    """Decide the type from the first bytes. Extensions are never consulted."""
    head = data[:8]
    for magic, input_type in _MAGIC:
        if head.startswith(magic):
            return input_type
    if head.startswith(_ZIP):
        return _sniff_zip(data)
    return _sniff_text(data)


def _sniff_text(data: bytes) -> InputType:
    sample = data[:4096].lstrip(b"\xef\xbb\xbf \t\r\n").lower()
    if sample.startswith(_HTML_MARKERS) or b"<html" in sample[:512]:
        return InputType.HTML
    if not _looks_like_text(sample):
        return InputType.UNKNOWN
    if sample.startswith(_MD_MARKERS) or b"\n# " in sample or b"\n## " in sample:
        return InputType.MARKDOWN
    return InputType.TEXT


def _looks_like_text(sample: bytes) -> bool:
    if not sample:
        return True
    try:
        sample.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return b"\x00" not in sample


def _sniff_zip(data: bytes) -> InputType:
    """OOXML is a zip whose [Content_Types].xml names the main part. Read names only."""
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            names = set(archive.namelist())
    except (zipfile.BadZipFile, OSError, RuntimeError, ValueError):
        return InputType.UNKNOWN
    if "[Content_Types].xml" not in names:
        return InputType.ZIP
    if any(name.startswith("word/") for name in names):
        return InputType.DOCX
    if any(name.startswith("ppt/") for name in names):
        return InputType.PPTX
    if any(name.startswith("xl/") for name in names):
        return InputType.XLSX
    return InputType.ZIP


def guard_size(data: bytes, limits: Limits, *, stage: int = 0) -> ParseFailure | None:
    """Reject before any parser sees the bytes."""
    if len(data) > limits.max_file_bytes:
        return ParseFailure(
            stage=stage,
            parser="ingest",
            reason="size",
            message=f"{len(data)} bytes exceeds the {limits.max_file_mb} MB cap",
        )
    return None


def guard_zip(data: bytes, limits: Limits, *, stage: int = 0) -> ParseFailure | None:
    """Zip-bomb guard from the central directory only: nothing is inflated here.

    Refuses too many entries, an uncompressed total more than max_zip_ratio times the
    compressed size, and nested archives.
    """
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            infos = archive.infolist()
    except (zipfile.BadZipFile, OSError, RuntimeError, ValueError) as exc:
        return ParseFailure(
            stage=stage, parser="zipfile", reason="crash", message=type(exc).__name__
        )
    if len(infos) > limits.max_zip_entries:
        return ParseFailure(
            stage=stage,
            parser="zipfile",
            reason="zip_ratio",
            message=f"{len(infos)} entries exceeds {limits.max_zip_entries}",
        )
    compressed = max(1, sum(info.compress_size for info in infos))
    uncompressed = sum(info.file_size for info in infos)
    if uncompressed > limits.max_zip_ratio * compressed:
        return ParseFailure(
            stage=stage,
            parser="zipfile",
            reason="zip_ratio",
            message=(
                f"uncompressed {uncompressed} is over {limits.max_zip_ratio}x "
                f"compressed {compressed}"
            ),
        )
    for info in infos:
        lowered = info.filename.lower()
        if lowered.endswith((".zip", ".docx", ".pptx", ".xlsx", ".jar")):
            return ParseFailure(
                stage=stage,
                parser="zipfile",
                reason="recursion",
                message=f"nested archive {info.filename!r} is not followed",
            )
    return None


def guard_pages(page_count: int, limits: Limits, *, stage: int = 0) -> ParseFailure | None:
    """Pages beyond the cap are not parsed; the report says so."""
    if page_count > limits.max_pages:
        return ParseFailure(
            stage=stage,
            parser="ingest",
            reason="pages",
            message=f"{page_count} pages exceeds the {limits.max_pages} page cap",
        )
    return None
