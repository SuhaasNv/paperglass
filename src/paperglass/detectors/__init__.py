"""One module per technique id, registered with @technique, emitting Candidates only.

Importing this package imports every detector module so the registry is complete.
"""

from paperglass.detectors import docx as _docx_detectors
from paperglass.detectors import pdf as _pdf_detectors
from paperglass.detectors import text as _text_detectors
from paperglass.detectors.base import Candidate, Detector
from paperglass.detectors.docx import color, part_hidden, vanish
from paperglass.detectors.docx import tiny as docx_tiny
from paperglass.detectors.pdf import (
    active_content,
    actualtext_override,
    annotation_hidden,
    covered,
    decoding_fallback,
    hidden_layer,
    low_contrast,
    metadata_payload,
    offpage,
    opacity,
    render_mode,
    tiny,
    tounicode_mismatch,
)
from paperglass.detectors.registry import (
    REGISTRY,
    SeverityDefault,
    TechniqueRegistry,
    TechniqueSpec,
    technique,
)
from paperglass.detectors.text import unicode_invisible

DETECTOR_MODULES = (
    active_content,
    actualtext_override,
    annotation_hidden,
    covered,
    decoding_fallback,
    hidden_layer,
    low_contrast,
    metadata_payload,
    offpage,
    opacity,
    render_mode,
    tiny,
    tounicode_mismatch,
    unicode_invisible,
    vanish,
    color,
    docx_tiny,
    part_hidden,
)
"""Every detector module, imported for its registration side effect."""

_PACKAGES = (_pdf_detectors, _docx_detectors, _text_detectors)

__all__ = [
    "DETECTOR_MODULES",
    "REGISTRY",
    "Candidate",
    "Detector",
    "SeverityDefault",
    "TechniqueRegistry",
    "TechniqueSpec",
    "technique",
]
