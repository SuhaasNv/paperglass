"""The instruction-likeness hook (docs/07-ai/CLASSIFIER_DESIGN.md).

A hint can only raise severity of a finding that is already hidden; it never creates one.
Core ships the profile phrase list. Anything else (Prompt Guard 2, LLM Guard, a custom
model) is a plug-in registered under the entry point group ``paperglass.hints``; core
never imports it, and every plug-in used is named in the report's rule versions.
"""

from __future__ import annotations

from functools import lru_cache
from importlib.metadata import entry_points
from typing import Protocol, runtime_checkable

from paperglass.engine.profile import Profile

ENTRY_POINT_GROUP = "paperglass.hints"


@runtime_checkable
class SeverityHint(Protocol):
    """What a plug-in provides. `score` returns instruction-likeness 0 to 1 for hidden text."""

    name: str
    version: str

    def score(self, text: str) -> float: ...


class PhraseHint:
    """The built-in hint: the profile's phrase list. Present so the interface has one user."""

    name = "phrases"

    def __init__(self, profile: Profile) -> None:
        self.profile = profile
        self.version = profile.version

    def score(self, text: str) -> float:
        lowered = text.casefold()
        hits = sum(1 for phrase in self.profile.phrases.instruction if phrase in lowered)
        return min(1.0, hits / 2.0)


@lru_cache(maxsize=1)
def installed_hints() -> tuple[SeverityHint, ...]:
    """Plug-ins found under the entry point group, instantiated once. Broken ones are skipped."""
    found: list[SeverityHint] = []
    for entry in entry_points(group=ENTRY_POINT_GROUP):
        try:
            candidate = entry.load()
            hint = candidate() if callable(candidate) else candidate
        except Exception:  # noqa: BLE001, S112  # a broken plug-in must not break a scan
            continue
        if isinstance(hint, SeverityHint):
            found.append(hint)
    return tuple(found)


def hints_for(profile: Profile) -> tuple[SeverityHint, ...]:
    return (PhraseHint(profile), *installed_hints())


def instruction_score(text: str, profile: Profile) -> tuple[float, str | None]:
    """The highest score across hints and the name of the hint that gave it."""
    best, who = 0.0, None
    for hint in hints_for(profile):
        try:
            score = float(hint.score(text))
        except Exception:  # noqa: BLE001, S112  # a plug-in failure is not a scan failure
            continue
        if score > best:
            best, who = score, hint.name
    return best, who
