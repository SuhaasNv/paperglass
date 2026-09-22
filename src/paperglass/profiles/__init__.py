"""Profiles: the TOML files (default, resume, peer-review, rag-ingest) and their models.

Shared by every layer: detectors read thresholds and allowlist limits, the engine reads
severity and verdict rules, adapters list the names.
"""

from paperglass.profiles._models import (
    Allowlist,
    Phrases,
    Profile,
    SeverityRules,
    Thresholds,
    VerdictRules,
    load_profile,
    profile_names,
)

__all__ = [
    "Allowlist",
    "Phrases",
    "Profile",
    "SeverityRules",
    "Thresholds",
    "VerdictRules",
    "load_profile",
    "profile_names",
]
