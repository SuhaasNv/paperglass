"""Profiles: every threshold a verdict depends on, loaded from the TOML files beside this module.

A profile may `extends` another: its tables are merged over the base, key by key, so a profile
states only what it changes (docs/04-report-design/REPORT_DESIGN.md, Profiles).
"""

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


MAX_EXTENDS_DEPTH = 4


def _raw(name: str) -> dict[str, object]:
    package = resources.files(PROFILE_PACKAGE)
    path = package / f"{name}.toml"
    if not path.is_file():
        known = sorted(p.name[:-5] for p in package.iterdir() if p.name.endswith(".toml"))
        msg = f"unknown profile {name!r}; known: {', '.join(known)}"
        raise KeyError(msg)
    with path.open("rb") as handle:
        return tomllib.load(handle)


def _merge(base: dict[str, object], override: dict[str, object]) -> dict[str, object]:
    merged = dict(base)
    for key, value in override.items():
        current = merged.get(key)
        if isinstance(current, dict) and isinstance(value, dict):
            merged[key] = _merge(current, value)
        elif isinstance(current, list) and isinstance(value, list):
            # Lists (phrases, verbs) extend the base; a profile adds cues, never removes them.
            merged[key] = current + [item for item in value if item not in current]
        else:
            merged[key] = value
    return merged


def _resolved(name: str, depth: int = 0) -> dict[str, object]:
    raw = _raw(name)
    parent = raw.pop("extends", None)
    if parent is None:
        return raw
    if not isinstance(parent, str) or depth >= MAX_EXTENDS_DEPTH:
        msg = f"profile {name!r}: extends must name a profile, at most {MAX_EXTENDS_DEPTH} deep"
        raise KeyError(msg)
    return _merge(_resolved(parent, depth + 1), raw)


@lru_cache(maxsize=8)
def load_profile(name: str = "default") -> Profile:
    """Read paperglass/profiles/<name>.toml. Unknown names raise KeyError with the known list."""
    profile = Profile.model_validate(_resolved(name))
    if profile.name != name:
        msg = f"profile file {name}.toml declares name {profile.name!r}"
        raise KeyError(msg)
    return profile


def profile_names() -> list[str]:
    package = resources.files(PROFILE_PACKAGE)
    return sorted(p.name[:-5] for p in package.iterdir() if p.name.endswith(".toml"))
