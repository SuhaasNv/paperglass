"""Sniffing, guards and limits (docs/03-architecture/SANDBOX.md)."""

from __future__ import annotations

import io
import zipfile

import pytest

from paperglass.ingest import (
    DepthExceededError,
    DepthGuard,
    InputType,
    Limits,
    guard_pages,
    guard_size,
    guard_zip,
    sniff,
)


def zip_bytes(entries: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in entries.items():
            archive.writestr(name, data)
    return buffer.getvalue()


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (b"%PDF-1.7\n%\xe2\xe3\xcf\xd3\n", InputType.PDF),
        (b"\x89PNG\r\n\x1a\n" + b"\x00" * 16, InputType.PNG),
        (b"\xff\xd8\xff\xe0" + b"\x00" * 16, InputType.JPG),
        (b"II*\x00" + b"\x00" * 16, InputType.TIFF),
        (b"MM\x00*" + b"\x00" * 16, InputType.TIFF),
        (b"<!DOCTYPE html><html><body>hi</body></html>", InputType.HTML),
        (b"  \n<html><head></head></html>", InputType.HTML),
        (b"# Title\n\nSome text.\n", InputType.MARKDOWN),
        (b"plain words only\n", InputType.TEXT),
        (b"", InputType.TEXT),
        (b"\x00\x01\x02binary\xff", InputType.UNKNOWN),
    ],
)
def test_sniff_by_magic_bytes(data: bytes, expected: InputType) -> None:
    assert sniff(data) is expected


def test_sniff_ooxml_by_content_types_and_main_part() -> None:
    ct = b"<Types/>"
    assert (
        sniff(zip_bytes({"[Content_Types].xml": ct, "word/document.xml": b"<w/>"}))
        is InputType.DOCX
    )
    assert (
        sniff(zip_bytes({"[Content_Types].xml": ct, "ppt/presentation.xml": b"<p/>"}))
        is InputType.PPTX
    )
    assert (
        sniff(zip_bytes({"[Content_Types].xml": ct, "xl/workbook.xml": b"<x/>"})) is InputType.XLSX
    )
    assert sniff(zip_bytes({"a.txt": b"x"})) is InputType.ZIP


def test_sniff_ignores_extension_like_content() -> None:
    assert sniff(b"this file is called resume.pdf but is text") is InputType.TEXT


def test_sniff_broken_zip_is_unknown() -> None:
    assert sniff(b"PK\x03\x04" + b"\xff" * 32) is InputType.UNKNOWN


def test_guard_size() -> None:
    limits = Limits(max_file_mb=1)
    assert guard_size(b"x" * 10, limits) is None
    failure = guard_size(b"x" * (1024 * 1024 + 1), limits)
    assert failure is not None
    assert failure.reason == "size"
    assert failure.technique_id == "parse.failure"


def test_guard_zip_accepts_a_normal_docx_shape() -> None:
    data = zip_bytes(
        {"[Content_Types].xml": b"<Types/>", "word/document.xml": b"<w>" + b"a" * 200 + b"</w>"}
    )
    assert guard_zip(data, Limits()) is None


def test_guard_zip_refuses_a_bomb_by_ratio() -> None:
    data = zip_bytes({"[Content_Types].xml": b"<Types/>", "word/document.xml": b"\x00" * 5_000_000})
    failure = guard_zip(data, Limits(max_zip_ratio=100))
    assert failure is not None
    assert failure.reason == "zip_ratio"


def test_guard_zip_refuses_too_many_entries() -> None:
    data = zip_bytes({f"f{i}.xml": b"x" for i in range(12)})
    failure = guard_zip(data, Limits(max_zip_entries=10))
    assert failure is not None
    assert failure.reason == "zip_ratio"


def test_guard_zip_refuses_nested_archives() -> None:
    data = zip_bytes({"[Content_Types].xml": b"<Types/>", "word/embeddings/inner.docx": b"PK"})
    failure = guard_zip(data, Limits())
    assert failure is not None
    assert failure.reason == "recursion"


def test_guard_zip_broken_archive_is_a_crash_failure() -> None:
    failure = guard_zip(b"PK\x03\x04garbage", Limits())
    assert failure is not None
    assert failure.reason == "crash"


def test_guard_pages() -> None:
    assert guard_pages(3, Limits(max_pages=3)) is None
    failure = guard_pages(4, Limits(max_pages=3))
    assert failure is not None
    assert failure.reason == "pages"


def test_limits_from_env_overrides() -> None:
    limits = Limits.from_env(
        {
            "PAPERGLASS_SANDBOX_SECONDS": "2.5",
            "PAPERGLASS_SANDBOX_MEMORY_MB": "128",
            "PAPERGLASS_MAX_FILE_MB": "7",
            "PAPERGLASS_MAX_PAGES": "9",
        }
    )
    assert limits.wall_seconds == 2.5
    assert limits.cpu_seconds == 2
    assert limits.memory_mb == 128
    assert limits.max_file_mb == 7
    assert limits.max_pages == 9
    assert Limits.from_env({}) == Limits()


def test_depth_guard() -> None:
    guard = DepthGuard(2)
    with guard, guard:
        assert guard.depth == 2
        with pytest.raises(DepthExceededError), guard:
            pass
    assert guard.depth == 0
    assert DepthGuard.failure("pikepdf").reason == "recursion"
