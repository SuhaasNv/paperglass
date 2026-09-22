"""Response shapes. The report itself is the library's Report JSON, unchanged."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ScanSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    expires_at: datetime
    file_name: str
    input_type: str
    verdict: str
    tier: str
    profile: str
    tool_version: str


class ScanDetail(ScanSummary):
    report: dict[str, object]
    fingerprint: dict[str, object] | None = None


class ScanList(BaseModel):
    scans: list[ScanSummary]


class TechniqueOut(BaseModel):
    id: str
    formats: list[str]
    views: list[str]
    stage: int
    self_proving: bool
    severity_class: str
    explanation: str
    threshold: str
    atr_rule: str | None
    rule_version: str
    release: str


class TechniqueList(BaseModel):
    techniques: list[TechniqueOut]
