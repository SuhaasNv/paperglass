"""Paperglass: see exactly what the model reads.

A document trust scanner and benchmark for AI pipelines. It shows the text a
document gives to a model (View A), compares it with the page it shows to a
person (View B) and with the document's structure (View C), and reports every
place the three differ, with evidence.

Public API lands story by story; see docs/05-planning/ISSUES.md.
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _version

try:
    __version__: str = _version("paperglass")
except PackageNotFoundError:  # pragma: no cover - only when run from an unbuilt checkout
    __version__ = "0.0.0+unknown"


def scan(data: bytes, **options: object) -> object:
    """Scan bytes and return a Report. Options: tier, profile, extractor, redact, limits.

    Imported lazily so `paperglass version` does not load the parsers.
    """
    from paperglass.engine import scan_bytes  # noqa: PLC0415

    return scan_bytes(data, **options)  # type: ignore[arg-type]  # options mirror scan_bytes


def fingerprint(data: bytes, **options: object) -> object:
    """Which installed extractors hand the hidden text to a model. Returns a Fingerprint."""
    from paperglass.engine import fingerprint_bytes  # noqa: PLC0415

    return fingerprint_bytes(data, **options)  # type: ignore[arg-type]  # options mirror it


__all__ = ["__version__", "fingerprint", "scan"]
