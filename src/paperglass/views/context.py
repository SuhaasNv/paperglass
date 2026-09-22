"""What a detector sees for one page: the extracted runs and the handles the views expose.

Grows per story (View A at US-006, View C at US-007, View B at US-030). Frozen so a
detector cannot mutate what another detector reads.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from paperglass.models import DocumentStructure, PageRaster, PageStructure, TextRun
from paperglass.models.docx import DocxStructure
from paperglass.profiles import Profile, load_profile


class PageContext(BaseModel):
    """Everything a detector may look at for one page."""

    model_config = ConfigDict(frozen=True, extra="forbid", arbitrary_types_allowed=True)

    page_number: int = Field(ge=1)
    page_count: int = Field(ge=1)
    input_type: str
    extractor: str
    runs: tuple[TextRun, ...] = ()
    """View A for this page."""
    width: float | None = Field(default=None, gt=0)
    height: float | None = Field(default=None, gt=0)
    structure: PageStructure | None = None
    """View C for this page (PDF only until US-034)."""
    document: DocumentStructure | None = None
    """Document-level View C (layers, metadata, active content); the same object on every page."""
    raster: PageRaster | None = None
    """View B raster for this page when stage 1 ran; stage 1 detectors read it."""
    docx: DocxStructure | None = None
    """View C for a DOCX (one page: Word documents are not paginated before layout)."""
    profile: Profile = Field(default_factory=load_profile)
    """Thresholds and allowlist limits the detectors read; the engine picks the profile."""
