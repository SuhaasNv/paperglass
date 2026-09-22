"""What View C returns for a DOCX: every run with the properties that decide visibility, and
the parts a person does not read in the body."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class DocxRun(_Frozen):
    paragraph: int = Field(ge=0)
    index: int = Field(ge=0)
    """Run index within the paragraph."""
    text: str
    vanish: bool = False
    spec_vanish: bool = False
    color: str | None = None
    """Hex RRGGBB from w:color, or None for automatic."""
    grey: float | None = Field(default=None, ge=0.0, le=1.0)
    size_pt: float | None = Field(default=None, ge=0.0)
    highlight: str | None = None
    shading_fill: str | None = None
    """Hex RRGGBB from w:shd, or None."""
    deleted: bool = False
    """Inside w:del (tracked deletion)."""
    inserted: bool = False
    field_code: bool = False
    """Inside a field instruction (w:instrText or w:fldSimple)."""


class DocxPart(_Frozen):
    kind: Literal[
        "comment",
        "footnote",
        "endnote",
        "header",
        "footer",
        "alt_text",
        "property",
        "field",
        "deleted",
    ]
    name: str
    """Part name or property key."""
    text: str


class DocxStructure(_Frozen):
    kind: Literal["docx"] = "docx"
    parser: str = "lxml"
    parser_version: str
    runs: tuple[DocxRun, ...] = ()
    parts: tuple[DocxPart, ...] = ()
    page_background: str | None = None
    """Hex RRGGBB from w:background, or None (white)."""
    has_macros: bool = False
