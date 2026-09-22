"""One module per technique id, registered with @technique, emitting Candidates only.

Importing this package imports every detector module so the registry is complete.
"""

from paperglass.detectors.base import Candidate, Detector
from paperglass.detectors.pdf import (  # noqa: F401  # registration side effects
    active_content,
    annotation_hidden,
    hidden_layer,
    low_contrast,
    metadata_payload,
    offpage,
    opacity,
    render_mode,
    tiny,
)
from paperglass.detectors.registry import (
    REGISTRY,
    SeverityDefault,
    TechniqueRegistry,
    TechniqueSpec,
    technique,
)
from paperglass.detectors.text import unicode_invisible  # noqa: F401

__all__ = [
    "REGISTRY",
    "Candidate",
    "Detector",
    "SeverityDefault",
    "TechniqueRegistry",
    "TechniqueSpec",
    "technique",
]
