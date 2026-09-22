"""The two-function adapter every detector implements (docs/08-benchmark/HARNESS.md).

    def scan(path: str) -> dict
        # {"verdict": str, "findings": [{"technique_id", "page", "bbox",
        #                                 "severity", "confidence"}]}
    def version() -> str

Paperglass's own adapter is `paperglass.bench.adapter.paperglass_detector`; a third-party
detector is named on the command line as `module:function` and must return the same shape.
"""

from __future__ import annotations

import importlib
import pathlib
from collections.abc import Callable
from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict, Field

FLAGGING_VERDICTS: frozenset[str] = frozenset({"suspicious", "malicious"})


class AdapterFinding(BaseModel):
    """One finding in adapter shape; the harness reads nothing else from a detector."""

    model_config = ConfigDict(extra="ignore")

    technique_id: str
    page: int | None = None
    bbox: tuple[float, float, float, float] | None = None
    severity: str = "medium"
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    status: str = "confirmed"
    """Detectors that distinguish possible from confirmed say so; others count as confirmed."""


class AdapterResult(BaseModel):
    model_config = ConfigDict(extra="ignore")

    verdict: str
    findings: list[AdapterFinding] = Field(default_factory=list)

    @property
    def flagged(self) -> bool:
        return self.verdict in FLAGGING_VERDICTS


@dataclass(frozen=True)
class Detector:
    name: str
    scan: Callable[[str], dict[str, object]]
    version: Callable[[], str]


def paperglass_scan(
    path: str, *, tier: str = "fast", profile: str = "default"
) -> dict[str, object]:
    from paperglass.engine import scan_bytes  # noqa: PLC0415  # bench stays light to import
    from paperglass.models import Tier  # noqa: PLC0415

    report = scan_bytes(pathlib.Path(path).read_bytes(), tier=Tier(tier), profile=profile)
    return {
        "verdict": report.verdict.value,
        "findings": [
            {
                "technique_id": f.technique_id,
                "page": f.page,
                "bbox": [f.bbox.x0, f.bbox.y0, f.bbox.x1, f.bbox.y1] if f.bbox else None,
                "severity": f.severity.value,
                "confidence": f.confidence,
                "status": f.status.value,
            }
            for f in report.findings
        ],
    }


def paperglass_version() -> str:
    from paperglass import __version__  # noqa: PLC0415

    return __version__


def paperglass_detector(*, tier: str = "fast", profile: str = "default") -> Detector:
    def scan(path: str) -> dict[str, object]:
        return paperglass_scan(path, tier=tier, profile=profile)

    return Detector(name=f"paperglass-{tier}", scan=scan, version=paperglass_version)


def load_detector(spec: str, *, tier: str = "fast", profile: str = "default") -> Detector:
    """`paperglass`, or `module:function` for any detector with a `version` beside it."""
    if spec == "paperglass":
        return paperglass_detector(tier=tier, profile=profile)
    module_name, _, function_name = spec.partition(":")
    if not module_name or not function_name:
        msg = f"detector {spec!r}: use 'paperglass' or 'module:function'"
        raise ValueError(msg)
    module = importlib.import_module(module_name)
    scan = getattr(module, function_name)
    version = getattr(module, "version", lambda: "unknown")
    return Detector(name=spec.replace(":", "."), scan=scan, version=version)
