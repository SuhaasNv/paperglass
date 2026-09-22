"""Severity class and level for a confirmed finding (docs/03-architecture/FINDING_SCHEMA.md)."""

from __future__ import annotations

import re

from paperglass.detectors import SeverityDefault, TechniqueSpec
from paperglass.engine.profile import Profile
from paperglass.models import Severity, SeverityClass

_WORD = re.compile(r"[a-z]+")


INSTRUCTION_SCORE = 0.5
"""A hint score at or above this makes a hidden run an instruction (never a finding alone)."""


def looks_like_instruction(text: str, profile: Profile) -> bool:
    from paperglass.engine.hints import instruction_score  # noqa: PLC0415  # avoids a cycle

    score, _ = instruction_score(text, profile)
    return score >= INSTRUCTION_SCORE


def names_an_action(text: str, profile: Profile) -> bool:
    words = set(_WORD.findall(text.casefold()))
    return any(verb in words for verb in profile.severity.instruction_critical_verbs)


def classify(spec: TechniqueSpec, text: str, profile: Profile) -> tuple[SeverityClass, Severity]:
    """The class from the registration, escalated by content, then the level from the profile."""
    default = spec.severity_class
    if default is SeverityDefault.STRUCTURE_ONLY:
        return SeverityClass.STRUCTURE_ONLY, profile.severity.structure_only
    if default is SeverityDefault.BENIGN_HIDDEN:
        return SeverityClass.BENIGN_HIDDEN, profile.severity.benign_hidden
    if default in (SeverityDefault.DATA, SeverityDefault.INSTRUCTION) and looks_like_instruction(
        text, profile
    ):
        level = (
            Severity.CRITICAL if names_an_action(text, profile) else profile.severity.instruction
        )
        return SeverityClass.INSTRUCTION, level
    if default is SeverityDefault.INSTRUCTION:
        return SeverityClass.INSTRUCTION, profile.severity.instruction
    return SeverityClass.DATA, profile.severity.data


def verdict_severity_map(profile: Profile) -> dict[Severity, str]:
    mapping: dict[Severity, str] = {}
    for level in profile.verdict.malicious:
        mapping[level] = "malicious"
    for level in profile.verdict.suspicious:
        mapping[level] = "suspicious"
    return mapping
