"""Profiles: every threshold a verdict depends on, loaded from TOML in paperglass/profiles."""

from __future__ import annotations

import tomllib
from functools import lru_cache
from importlib import resources

from pydantic import BaseModel, ConfigDict, Field

from paperglass.models import Severity

PROFILE_PACKAGE = "paperglass.profiles"


class Thresholds(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    contrast: float = Field(gt=0, lt=1)
    tiny_pt: float = Field(gt=0)
    alpha: float = Field(gt=0, lt=1)
    ink_fraction_visible: float = Field(gt=0, lt=1)
    ink_fraction_invisible: float = Field(ge=0, lt=1)
    ocr_agreement_hidden: float = Field(ge=0, le=1)
    ocr_agreement_benign: float = Field(ge=0, le=1)


class Allowlist(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    alt_text_max_chars: int = Field(ge=0)
    actual_text_max_chars: int = Field(ge=0)
    properties_max_chars: int = Field(ge=0)
    ocr_layer_min_agreement: float = Field(ge=0, le=1)


class SeverityRules(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", populate_by_name=True)

    instruction: Severity
    data: Severity
    benign_hidden: Severity = Field(alias="benign-hidden")
    structure_only: Severity = Field(alias="structure-only")
    instruction_critical_verbs: tuple[str, ...]


class VerdictRules(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    malicious: tuple[Severity, ...]
    suspicious: tuple[Severity, ...]
    parse_failure_verdict: str


class Phrases(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    instruction: tuple[str, ...]


class Profile(BaseModel):
    """A named set of thresholds; the name goes into every report."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    version: str
    thresholds: Thresholds
    allowlist: Allowlist
    severity: SeverityRules
    verdict: VerdictRules
    phrases: Phrases


@lru_cache(maxsize=8)
def load_profile(name: str = "default") -> Profile:
    """Read paperglass/profiles/<name>.toml. Unknown names raise KeyError with the known list."""
    package = resources.files(PROFILE_PACKAGE)
    path = package / f"{name}.toml"
    if not path.is_file():
        known = sorted(p.name[:-5] for p in package.iterdir() if p.name.endswith(".toml"))
        msg = f"unknown profile {name!r}; known: {', '.join(known)}"
        raise KeyError(msg)
    with path.open("rb") as handle:
        return Profile.model_validate(tomllib.load(handle))


def profile_names() -> list[str]:
    package = resources.files(PROFILE_PACKAGE)
    return sorted(p.name[:-5] for p in package.iterdir() if p.name.endswith(".toml"))
