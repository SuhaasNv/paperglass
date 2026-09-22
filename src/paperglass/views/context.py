"""What a detector sees for one page: the extracted runs and the handles the views expose.

Grows per story (View A at US-006, View C at US-007, View B at US-030). Frozen so a
detector cannot mutate what another detector reads.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from paperglass.models import BBox


class TextRun(BaseModel):
    """One positioned run of text as an extractor returned it (View A)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    text: str
    bbox: BBox | None = None
    font: str | None = None
    size_pt: float | None = Field(default=None, ge=0.0)
    offset: int | None = Field(default=None, ge=0)
    """Content-stream byte offset (PDF) or run index within the part (OOXML)."""


class PageContext(BaseModel):
    """Everything a detector may look at for one page."""

    model_config = ConfigDict(frozen=True, extra="forbid", arbitrary_types_allowed=True)

    page_number: int = Field(ge=1)
    page_count: int = Field(ge=1)
    input_type: str
    extractor: str
    runs: tuple[TextRun, ...] = ()
