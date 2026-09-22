"""What `paperglass fingerprint` returns: per hidden run, which extractors hand it to a model."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ExtractorVerdict(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    extractor: str
    version: str
    returns_hidden_text: bool | None
    """True when the extractor's text contains the hidden run; None when the extractor failed."""
    agreement: float = Field(ge=0.0, le=1.0)


class FingerprintRow(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    finding_id: str
    technique_id: str
    page: int | None
    text_preview: str
    extractors: tuple[ExtractorVerdict, ...]


class Fingerprint(BaseModel):
    """One row per confirmed finding of the default scan, one column per installed extractor."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    input_sha256: str
    input_type: str
    default_extractor: str
    extractors: dict[str, str]
    """Extractor name to version, every one that ran."""
    failed: dict[str, str] = Field(default_factory=dict)
    """Extractor name to failure reason."""
    rows: tuple[FingerprintRow, ...]

    @property
    def fooled(self) -> dict[str, int]:
        """How many hidden runs each extractor returns."""
        counts = dict.fromkeys(self.extractors, 0)
        for row in self.rows:
            for verdict in row.extractors:
                if verdict.returns_hidden_text:
                    counts[verdict.extractor] += 1
        return counts
