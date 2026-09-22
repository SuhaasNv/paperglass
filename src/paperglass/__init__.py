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

__all__ = ["__version__"]
