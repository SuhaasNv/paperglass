"""View A: pluggable extractors returning positioned text runs.

The default is pypdfium2 (what most viewers and many pipelines use). Others are listed so
`paperglass fingerprint` (US-023) can show which backends return a hidden run. Docling and
OpenDataLoader are added there.
"""

from __future__ import annotations

from paperglass.ingest.sniff import InputType
from paperglass.parsers import pdf_text, plain_text
from paperglass.views.extract.base import Extractor, ExtractOutcome

PDF = frozenset({InputType.PDF})
TEXT = frozenset({InputType.TEXT, InputType.MARKDOWN})

EXTRACTORS: dict[str, Extractor] = {
    "pypdfium2": Extractor("pypdfium2", "pypdfium2", PDF, pdf_text.pypdfium2_extract),
    "pdfplumber": Extractor("pdfplumber", "pdfplumber", PDF, pdf_text.pdfplumber_extract),
    "pypdf": Extractor("pypdf", "pypdf", PDF, pdf_text.pypdf_extract),
    "pdfminer.six": Extractor("pdfminer.six", "pdfminer.six", PDF, pdf_text.pdfminer_extract),
    "plain": Extractor("plain", "paperglass", TEXT, plain_text.plain_extract),
}

DEFAULT_EXTRACTOR = "pypdfium2"
DEFAULTS: dict[InputType, str] = {
    InputType.PDF: "pypdfium2",
    InputType.TEXT: "plain",
    InputType.MARKDOWN: "plain",
}


def available(input_type: InputType | None = None) -> list[Extractor]:
    """Installed backends, optionally filtered by input type, default first."""
    found = [
        extractor
        for extractor in EXTRACTORS.values()
        if extractor.available() and (input_type is None or input_type in extractor.input_types)
    ]
    found.sort(key=lambda e: (e.name != DEFAULT_EXTRACTOR, e.name))
    return found


def default_for(input_type: InputType) -> Extractor | None:
    name = DEFAULTS.get(input_type)
    return EXTRACTORS[name] if name else None


def get(name: str) -> Extractor:
    try:
        return EXTRACTORS[name]
    except KeyError as exc:
        msg = f"unknown extractor {name!r}; known: {', '.join(EXTRACTORS)}"
        raise KeyError(msg) from exc


__all__ = [
    "DEFAULTS",
    "DEFAULT_EXTRACTOR",
    "EXTRACTORS",
    "ExtractOutcome",
    "Extractor",
    "available",
    "default_for",
    "get",
]
