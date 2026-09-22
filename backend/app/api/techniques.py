"""GET /api/v1/techniques: the registry, the single source the techniques page renders."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.schemas import TechniqueList, TechniqueOut
from paperglass.detectors import REGISTRY

router = APIRouter(prefix="/api/v1/techniques", tags=["techniques"])


@router.get("", response_model=TechniqueList)
def list_techniques() -> TechniqueList:
    return TechniqueList(
        techniques=[
            TechniqueOut(
                id=spec.id,
                formats=list(spec.formats),
                views=list(spec.views),
                stage=spec.stage,
                self_proving=spec.self_proving,
                severity_class=spec.severity_class.value,
                explanation=spec.explanation,
                threshold=spec.threshold,
                atr_rule=spec.atr_rule,
                rule_version=spec.rule_version,
                release=spec.release,
            )
            for spec in sorted(REGISTRY.specs().values(), key=lambda s: s.id)
        ]
    )
