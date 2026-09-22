"""View C: structural probes per format, emitting candidates with a named mechanism.

`pdf_structure(data, limits=)` walks the PDF inside the sandbox and returns a
DocumentStructure (or a ParseFailure). Detectors read the result; nothing here decides.
"""

from __future__ import annotations

from dataclasses import dataclass

from paperglass.ingest import Limits, run_sandboxed
from paperglass.models import ParseFailure
from paperglass.models.structure import DocumentStructure
from paperglass.parsers import pdf_structure as _pdf


@dataclass(frozen=True)
class StructureOutcome:
    structure: DocumentStructure | None
    failure: ParseFailure | None

    @property
    def ok(self) -> bool:
        return self.failure is None


def pdf_structure(data: bytes, *, limits: Limits, stage: int = 0) -> StructureOutcome:
    result = run_sandboxed(
        _pdf.pikepdf_structure, (data,), limits=limits, parser="pikepdf", stage=stage
    )
    if result.failure is not None or result.value is None:
        failure = result.failure or ParseFailure(
            stage=stage, parser="pikepdf", reason="crash", message="no structure returned"
        )
        return StructureOutcome(structure=None, failure=failure)
    return StructureOutcome(structure=result.value, failure=None)


__all__ = ["StructureOutcome", "pdf_structure"]
