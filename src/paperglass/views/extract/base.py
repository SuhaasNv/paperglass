"""The Extractor protocol: a named backend turning bytes into DocumentText inside the sandbox."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError, version

from paperglass.ingest import Limits, run_sandboxed
from paperglass.ingest.sniff import InputType
from paperglass.models import DocumentText, ParseFailure


@dataclass(frozen=True)
class ExtractOutcome:
    """Either the document text or the failure that stopped extraction."""

    document: DocumentText | None
    failure: ParseFailure | None

    @property
    def ok(self) -> bool:
        return self.failure is None


@dataclass(frozen=True)
class Extractor:
    """One View A backend. `function` is a module-level callable in paperglass.parsers."""

    name: str
    distribution: str
    """The installed distribution whose presence makes this backend available."""
    input_types: frozenset[InputType]
    function: Callable[[bytes], DocumentText]

    def available(self) -> bool:
        try:
            version(self.distribution)
        except PackageNotFoundError:
            return False
        return True

    def version(self) -> str:
        try:
            return version(self.distribution)
        except PackageNotFoundError:
            return "unknown"

    def extract(self, data: bytes, *, limits: Limits, stage: int = 0) -> ExtractOutcome:
        result = run_sandboxed(self.function, (data,), limits=limits, parser=self.name, stage=stage)
        if result.failure is not None or result.value is None:
            failure = result.failure or ParseFailure(
                stage=stage, parser=self.name, reason="crash", message="no document returned"
            )
            return ExtractOutcome(document=None, failure=failure)
        return ExtractOutcome(document=result.value, failure=None)
