"""The technique registry: the single source for ids, explanations, thresholds and ATR mappings.

Rules are in docs/03-architecture/TECHNIQUE_REGISTRY.md. tests/unit/test_registry.py checks
that every registered id has a THREATS.md row with the same sentence and threshold and a
fixture pair under tests/fixtures.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterator, Mapping
from enum import StrEnum
from typing import Final, Literal

from pydantic import BaseModel, ConfigDict, Field

from paperglass.detectors.base import Detector
from paperglass.models import SeverityClass

TECHNIQUE_ID: Final = re.compile(r"^[a-z]+(\.[a-z_0-9]+)+$")

Format = Literal["pdf", "docx", "pptx", "html", "md", "png", "jpg", "tiff", "any"]
View = Literal["A", "B", "C"]


class SeverityDefault(StrEnum):
    """The class a technique's candidates start with, before escalation or profile overrides."""

    INSTRUCTION = SeverityClass.INSTRUCTION.value
    DATA = SeverityClass.DATA.value
    BENIGN_HIDDEN = SeverityClass.BENIGN_HIDDEN.value
    STRUCTURE_ONLY = SeverityClass.STRUCTURE_ONLY.value
    MODIFIER = "modifier"
    """Raises severity of another finding; can never produce a finding on its own."""


class TechniqueSpec(BaseModel):
    """Everything THREATS.md and the report need to know about one technique."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(pattern=TECHNIQUE_ID.pattern)
    formats: tuple[Format, ...] = Field(min_length=1)
    views: tuple[View, ...] = Field(min_length=1)
    stage: int = Field(ge=0, le=4)
    self_proving: bool = False
    severity_class: SeverityDefault
    explanation: str = Field(min_length=1)
    """The plain-language sentence shown in the report; identical to the THREATS.md row."""
    threshold: str = Field(min_length=1)
    """The documented threshold or mechanism, as text; the number itself lives in the profile."""
    atr_rule: str | None = None
    rule_version: str = Field(pattern=r"^\d+$")
    release: str = Field(pattern=r"^v\d+\.\d+\.\d+$")


class TechniqueRegistry:
    """Ordered, write-once mapping from technique id to (spec, detector class)."""

    def __init__(self) -> None:
        self._specs: dict[str, TechniqueSpec] = {}
        self._detectors: dict[str, type[Detector]] = {}

    def register(self, spec: TechniqueSpec, detector: type[object]) -> None:
        if spec.id in self._specs:
            msg = f"technique {spec.id} is already registered; one detector, one id"
            raise ValueError(msg)
        if not issubclass(detector, Detector):
            msg = f"{detector.__name__} must subclass Detector"
            raise TypeError(msg)
        self._specs[spec.id] = spec
        self._detectors[spec.id] = detector

    def spec(self, technique_id: str) -> TechniqueSpec:
        return self._specs[technique_id]

    def detector(self, technique_id: str) -> type[Detector]:
        return self._detectors[technique_id]

    def specs(self) -> Mapping[str, TechniqueSpec]:
        return dict(self._specs)

    def rule_versions(self) -> dict[str, str]:
        """The map every report carries."""
        return {technique_id: spec.rule_version for technique_id, spec in self._specs.items()}

    def __contains__(self, technique_id: object) -> bool:
        return technique_id in self._specs

    def __iter__(self) -> Iterator[str]:
        return iter(self._specs)

    def __len__(self) -> int:
        return len(self._specs)


REGISTRY: Final = TechniqueRegistry()


def technique(  # noqa: PLR0913  # one keyword per spec field is the point of the decorator
    *,
    id: str,
    formats: tuple[Format, ...],
    views: tuple[View, ...],
    stage: int,
    severity_class: SeverityDefault,
    explanation: str,
    threshold: str,
    rule_version: str,
    release: str,
    self_proving: bool = False,
    atr_rule: str | None = None,
    registry: TechniqueRegistry = REGISTRY,
) -> Callable[[type[Detector]], type[Detector]]:
    """Register a Detector subclass under one technique id.

    Usage: see docs/03-architecture/TECHNIQUE_REGISTRY.md. The decorator attaches the spec
    to the class as ``spec`` and adds it to the registry at import time.
    """
    spec = TechniqueSpec(
        id=id,
        formats=formats,
        views=views,
        stage=stage,
        self_proving=self_proving,
        severity_class=severity_class,
        explanation=explanation,
        threshold=threshold,
        atr_rule=atr_rule,
        rule_version=rule_version,
        release=release,
    )

    def decorate(cls: type[Detector]) -> type[Detector]:
        registry.register(spec, cls)
        cls.spec = spec  # type: ignore[attr-defined]  # attached for the engine and the report
        return cls

    return decorate
