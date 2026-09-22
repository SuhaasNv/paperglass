"""What View A returns: pages of positioned text runs, extractor-agnostic."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from paperglass.models.schema import BBox


class TextRun(BaseModel):
    """One positioned run of text as an extractor returned it."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    text: str
    bbox: BBox | None = None
    font: str | None = None
    size_pt: float | None = Field(default=None, ge=0.0)
    offset: int | None = Field(default=None, ge=0)
    """Character index in the page's text (pypdfium2), object index (pdfminer), or None."""


class PageText(BaseModel):
    """One page of View A."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    number: int = Field(ge=1)
    width: float = Field(gt=0)
    height: float = Field(gt=0)
    runs: tuple[TextRun, ...] = ()

    @property
    def text(self) -> str:
        return "\n".join(run.text for run in self.runs)


class DocumentText(BaseModel):
    """View A for a whole document, from one named extractor."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    extractor: str
    extractor_version: str
    pages: tuple[PageText, ...] = ()

    @property
    def page_count(self) -> int:
        return len(self.pages)

    @property
    def text(self) -> str:
        return "\n\n".join(page.text for page in self.pages)
