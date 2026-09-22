"""What a detector sees for one page: the extracted runs and the handles the views expose.

Grows per story (View A at US-006, View C at US-007, View B at US-030). Frozen so a
detector cannot mutate what another detector reads.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from paperglass.models import TextRun


class PageContext(BaseModel):
    """Everything a detector may look at for one page."""

    model_config = ConfigDict(frozen=True, extra="forbid", arbitrary_types_allowed=True)

    page_number: int = Field(ge=1)
    page_count: int = Field(ge=1)
    input_type: str
    extractor: str
    runs: tuple[TextRun, ...] = ()
    width: float | None = Field(default=None, gt=0)
    height: float | None = Field(default=None, gt=0)
