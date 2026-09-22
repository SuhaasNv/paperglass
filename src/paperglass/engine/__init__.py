"""Alignment, promotion from possible to confirmed, severity classes, allowlist
constraints, verdict, clean().
"""

from paperglass.detectors import REGISTRY, TechniqueSpec
from paperglass.engine.fingerprint import fingerprint_bytes
from paperglass.engine.hints import SeverityHint, hints_for, instruction_score
from paperglass.engine.profile import Profile, load_profile, profile_names
from paperglass.engine.scan import scan_bytes


def technique_specs() -> dict[str, TechniqueSpec]:
    """The registered technique specs by id, for layers above the engine (bench, adapters)."""
    return dict(REGISTRY.specs())


__all__ = [
    "Profile",
    "SeverityHint",
    "fingerprint_bytes",
    "hints_for",
    "instruction_score",
    "load_profile",
    "profile_names",
    "scan_bytes",
    "technique_specs",
]
