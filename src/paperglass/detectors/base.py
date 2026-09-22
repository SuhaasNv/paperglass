"""The detector contract: probe a page, emit candidates, never dicts, never exceptions."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable

from pydantic import BaseModel, ConfigDict, Field

from paperglass.models import BBox
from paperglass.views.context import PageContext


class Candidate(BaseModel):
    """A View C or View A observation before the engine confirms it and sets severity.

    A candidate always names its mechanism and a reproduce command; the engine refuses one
    without them (docs/03-architecture/TECHNIQUE_REGISTRY.md).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    technique_id: str
    page: int | None = Field(default=None, ge=1)
    bbox: BBox | None = None
    extracted_text: str = ""
    mechanism: str = Field(min_length=1)
    reproduce: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    self_proving: bool = False
    """True when the mechanism alone proves hiding (Tr 3 with text, OCG OFF, w:vanish)."""


class Detector(ABC):
    """One technique id, one class. Registered with @technique."""

    @abstractmethod
    def probe(self, ctx: PageContext) -> Iterable[Candidate]:
        """Return every candidate on this page. Must not raise; the sandbox owns failures."""
