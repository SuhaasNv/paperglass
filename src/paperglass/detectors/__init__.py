"""One module per technique id, registered with @technique, emitting Candidates only.

Importing this package imports every detector module so the registry is complete.
Modules are added here as their stories land (docs/05-planning/ISSUES.md).
"""

from paperglass.detectors.base import Candidate, Detector
from paperglass.detectors.registry import (
    REGISTRY,
    SeverityDefault,
    TechniqueRegistry,
    TechniqueSpec,
    technique,
)

__all__ = [
    "REGISTRY",
    "Candidate",
    "Detector",
    "SeverityDefault",
    "TechniqueRegistry",
    "TechniqueSpec",
    "technique",
]
