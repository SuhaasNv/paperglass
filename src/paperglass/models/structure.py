"""What View C returns for a PDF: every text object with the state that decides whether a
person can see it, plus the document-level carriers (fonts, layers, annotations, metadata,
active content). Extractor-agnostic and picklable, so it crosses the sandbox boundary.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from paperglass.models.schema import BBox


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class PdfColour(_Frozen):
    """A fill colour reduced to a grey level 0 to 1 when it can be, plus the raw operator."""

    operator: str
    components: tuple[float, ...]
    grey: float | None = Field(default=None, ge=0.0, le=1.0)
    """Approximate luminance 0 (black) to 1 (white) for device spaces; None when unknown."""


class PdfTextObject(_Frozen):
    """One text-showing operation (Tj, TJ, ', ") with the graphics state in force."""

    instruction: int = Field(ge=0)
    """Index of the instruction in the page's parsed content stream (the mechanism locator)."""
    text: str
    raw_bytes: int = Field(ge=0)
    font_resource: str | None = None
    font_size: float | None = None
    """Effective size after the text and current transformation matrices."""
    render_mode: int = Field(default=0, ge=0, le=7)
    fill: PdfColour | None = None
    fill_alpha: float = Field(default=1.0, ge=0.0, le=1.0)
    blend_mode: str | None = None
    origin: tuple[float, float]
    """Start of the text in user space (after Tm and CTM)."""
    bbox: BBox | None = None
    """Approximate: origin, the font size and a width estimate; the raster (View B) refines it."""
    clip: BBox | None = None
    """The current clip rectangle when one was set with re W n, in user space."""
    ocg: str | None = None
    """Name of the optional content group in force, if any."""
    ocg_hidden: bool = False
    actual_text: str | None = None
    marked_content_depth: int = Field(default=0, ge=0)


class PdfFontInfo(_Frozen):
    resource: str
    base_font: str | None = None
    subtype: str | None = None
    has_to_unicode: bool = False
    embedded: bool = False
    is_type3: bool = False
    is_type0: bool = False
    encoding: str | None = None
    object_number: int | None = None


class PdfAnnotation(_Frozen):
    subtype: str | None = None
    hidden: bool = False
    no_view: bool = False
    contents: str | None = None
    field_value: str | None = None
    rect: BBox | None = None
    has_javascript: bool = False
    object_number: int | None = None


class PageStructure(_Frozen):
    number: int = Field(ge=1)
    width: float = Field(gt=0)
    height: float = Field(gt=0)
    crop_box: BBox | None = None
    content_object: int | None = None
    text_objects: tuple[PdfTextObject, ...] = ()
    fonts: tuple[PdfFontInfo, ...] = ()
    annotations: tuple[PdfAnnotation, ...] = ()
    parse_note: str | None = None
    """Set when the content stream could not be fully walked; the page is still reported."""


class PdfMetadata(_Frozen):
    info: dict[str, str] = Field(default_factory=dict)
    xmp_length: int = Field(default=0, ge=0)
    xmp_text: str | None = None


class DocumentStructure(_Frozen):
    kind: Literal["pdf"] = "pdf"
    parser: str = "pikepdf"
    parser_version: str
    page_count: int = Field(ge=0)
    pages: tuple[PageStructure, ...] = ()
    ocgs_off: tuple[str, ...] = ()
    """Optional content groups in the default configuration's OFF array, by name."""
    ocgs_all: tuple[str, ...] = ()
    metadata: PdfMetadata = Field(default_factory=PdfMetadata)
    has_javascript: bool = False
    has_open_action: bool = False
    has_additional_actions: bool = False
    embedded_files: tuple[str, ...] = ()
    encrypted: bool = False
