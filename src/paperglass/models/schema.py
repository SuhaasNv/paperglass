"""Finding and Report models, schema version 1.

The contract is in docs/03-architecture/FINDING_SCHEMA.md. Any field added,
removed or re-typed bumps SCHEMA_VERSION, amends that document, regenerates the
golden files under tests/golden and records the reason in the commit body.

Models are frozen so a report cannot drift after it is built, and serialise
with sorted keys so the same input always gives the same bytes.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from enum import StrEnum
from typing import Final, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

SCHEMA_VERSION: Final = 2
"""v2 (22 Sep 2026, US-043) adds `pages`; a v2 reader accepts a v1 report, whose pages are empty."""

# The technique id under which a parser crash, timeout or limit hit is reported.
PARSE_FAILURE_TECHNIQUE: Final = "parse.failure"


class Severity(StrEnum):
    """Severity of a finding after the severity class and the profile have applied."""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SeverityClass(StrEnum):
    """Why a finding has the severity it has (docs/03-architecture/FINDING_SCHEMA.md)."""

    INSTRUCTION = "instruction"
    DATA = "data"
    BENIGN_HIDDEN = "benign-hidden"
    STRUCTURE_ONLY = "structure-only"


class FindingStatus(StrEnum):
    """A View C candidate is possible until View B or a self-proving mechanism confirms it."""

    POSSIBLE = "possible"
    CONFIRMED = "confirmed"


class Verdict(StrEnum):
    """The four verdicts. There is no numeric score (ADR-004)."""

    CLEAN = "clean"
    BENIGN_HIDDEN = "benign-hidden"
    SUSPICIOUS = "suspicious"
    MALICIOUS = "malicious"


class Tier(StrEnum):
    """Which cascade stages ran (docs/03-architecture/VIEWS.md)."""

    FAST = "fast"
    STANDARD = "standard"
    DEEP = "deep"


View = Literal["A", "B", "C"]
Provenance = Literal["visible-confirmed", "benign-hidden", "structure-only", "removed"]

# Severity order used by the verdict rules and by report sorting.
SEVERITY_ORDER: Mapping[Severity, int] = {
    Severity.INFO: 0,
    Severity.LOW: 1,
    Severity.MEDIUM: 2,
    Severity.HIGH: 3,
    Severity.CRITICAL: 4,
}


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", str_strip_whitespace=False)


class BBox(_Frozen):
    """A region on a page in PDF points, origin bottom-left, x0 <= x1 and y0 <= y1."""

    x0: float
    y0: float
    x1: float
    y1: float

    @model_validator(mode="after")
    def _ordered(self) -> BBox:
        if self.x1 < self.x0 or self.y1 < self.y0:
            msg = f"bbox must be ordered: ({self.x0}, {self.y0}, {self.x1}, {self.y1})"
            raise ValueError(msg)
        return self


class RenderCrop(_Frozen):
    """The rendered region as a PNG data URI, or a reason why there is none."""

    data_uri: str | None = None
    none_reason: str | None = None

    @model_validator(mode="after")
    def _one_of(self) -> RenderCrop:
        if (self.data_uri is None) == (self.none_reason is None):
            msg = "exactly one of data_uri or none_reason must be set"
            raise ValueError(msg)
        return self


class Finding(_Frozen):
    """One thing the model would read that a person would not see, with its evidence."""

    id: str = Field(pattern=r"^f-\d+$")
    technique_id: str = Field(pattern=r"^[a-z]+(\.[a-z_0-9]+)+$")
    status: FindingStatus
    page: int | None = Field(default=None, ge=1)
    bbox: BBox | None = None
    extracted_text: str
    render_crop: RenderCrop
    why_hidden: str = Field(min_length=1)
    mechanism: str = Field(min_length=1)
    reproduce: str = Field(min_length=1)
    severity: Severity
    severity_class: SeverityClass
    confidence: float = Field(ge=0.0, le=1.0)
    views: tuple[View, ...] = Field(min_length=1)
    stage: int = Field(ge=0, le=4)
    atr_rule: str | None = None
    extractor: str = Field(min_length=1)

    @field_validator("views")
    @classmethod
    def _views_unique_and_sorted(cls, views: tuple[View, ...]) -> tuple[View, ...]:
        ordered = tuple(sorted(set(views)))
        return ordered


class ParseFailure(_Frozen):
    """A parser crash, timeout or limit hit. Reported, never raised (SANDBOX.md)."""

    technique_id: Literal["parse.failure"] = PARSE_FAILURE_TECHNIQUE
    stage: int = Field(ge=0, le=4)
    parser: str = Field(min_length=1)
    reason: Literal["crash", "timeout", "memory", "cpu", "size", "pages", "zip_ratio", "recursion"]
    message: str = ""


RunStatus = Literal["visible", "hidden", "benign-hidden", "unverified"]


class RunView(_Frozen):
    """One extracted run as the diff shows it: text, place, and whether the page shows it."""

    text: str
    bbox: BBox | None = None
    status: RunStatus
    """visible: ink where the run is; hidden: a confirmed finding; benign-hidden: allowed by a
    public rule; unverified: no raster, no position, or the ink check could not decide."""
    finding_id: str | None = Field(default=None, pattern=r"^f-\d+$")


class PageView(_Frozen):
    """One page as the report shows it: size, a thumbnail of what a person sees, every run."""

    number: int = Field(ge=1)
    width_pt: float | None = Field(default=None, gt=0)
    height_pt: float | None = Field(default=None, gt=0)
    thumbnail: RenderCrop
    """A JPEG data URI of the rendered page, or none with a reason (no raster, redact, cap)."""
    runs: tuple[RunView, ...]


class Report(_Frozen):
    """The scan result. JSON output is deterministic for the same input and tool version."""

    schema_version: Literal[1, 2] = SCHEMA_VERSION
    tool_version: str = Field(min_length=1)
    rule_versions: dict[str, str]
    input_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    input_type: str = Field(min_length=1)
    extractor: str = Field(min_length=1)
    tier: Tier
    profile: str = Field(min_length=1)
    page_count: int = Field(ge=0)
    pages_render_verified: int = Field(ge=0)
    dpi: int | None = Field(default=None, ge=1)
    verdict: Verdict
    severity_counts: dict[Severity, int]
    findings: tuple[Finding, ...]
    pages: tuple[PageView, ...] = ()
    """Empty in a v1 report and for a document with no pages."""
    parse_failures: tuple[ParseFailure, ...] = ()
    network_used: tuple[str, ...] = ()
    timing_ms: dict[str, float]

    @model_validator(mode="after")
    def _consistent(self) -> Report:
        if self.pages_render_verified > self.page_count:
            msg = "pages_render_verified cannot exceed page_count"
            raise ValueError(msg)
        ids = [finding.id for finding in self.findings]
        if len(ids) != len(set(ids)):
            msg = "finding ids must be unique within a report"
            raise ValueError(msg)
        return self

    def to_json(self) -> str:
        """Canonical JSON: sorted keys, no trailing whitespace, newline at the end."""
        payload = self.model_dump(mode="json")
        return json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False) + "\n"

    @classmethod
    def from_json(cls, text: str) -> Report:
        return cls.model_validate_json(text)


class Run(_Frozen):
    """One run of the cleaned text with its provenance tag (VIEWS.md, clean())."""

    text: str
    provenance: Provenance
    page: int | None = Field(default=None, ge=1)
    finding_id: str | None = Field(default=None, pattern=r"^f-\d+$")


class CleanResult(_Frozen):
    """The subtractive clean() result (ADR-005)."""

    text: str
    runs: tuple[Run, ...]
    words_kept: int = Field(ge=0)
    words_removed: int = Field(ge=0)
    fidelity: float = Field(ge=0.0, le=1.0)
    policy_applied: Literal["pass", "clean", "block"]
    report: Report


class Receipt(_Frozen):
    """What the MCP and REST adapters hand back so a caller can prove a file was scanned."""

    input_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    verdict: Verdict
    severity_counts: dict[Severity, int]
    rule_versions: dict[str, str]
    tool_version: str
    pages_render_verified: int = Field(ge=0)
    issued_at: str = Field(min_length=1)


def sha256_of(data: bytes) -> str:
    """The input hash carried in every report."""
    return hashlib.sha256(data).hexdigest()


def severity_counts_of(findings: Sequence[Finding]) -> dict[Severity, int]:
    """Counts over confirmed findings only, every severity present so the shape is stable."""
    counts: dict[Severity, int] = dict.fromkeys(Severity, 0)
    for finding in findings:
        if finding.status is FindingStatus.CONFIRMED:
            counts[finding.severity] += 1
    return counts


def verdict_of(findings: Sequence[Finding], parse_failures: Sequence[ParseFailure] = ()) -> Verdict:
    """The default-profile verdict rules from FINDING_SCHEMA.md, over confirmed findings only.

    A parse failure alone yields suspicious: a file the scanner cannot read is a file
    a person could not review.
    """
    confirmed = [f for f in findings if f.status is FindingStatus.CONFIRMED]
    if any(f.severity in (Severity.HIGH, Severity.CRITICAL) for f in confirmed):
        return Verdict.MALICIOUS
    if any(f.severity is Severity.MEDIUM for f in confirmed) or parse_failures:
        return Verdict.SUSPICIOUS
    if any(f.severity_class is SeverityClass.BENIGN_HIDDEN for f in confirmed):
        return Verdict.BENIGN_HIDDEN
    return Verdict.CLEAN


def json_schema() -> dict[str, object]:
    """The JSON schema for Report; scripts/export_schema.py writes schemas/report-v1.json."""
    return Report.model_json_schema()
