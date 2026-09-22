"""GET /api/v1/profiles: the profiles the upload form offers, with a sentence each."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.schemas import ProfileList, ProfileOut
from paperglass.profiles import load_profile, profile_names

router = APIRouter(prefix="/api/v1/profiles", tags=["profiles"])

DESCRIPTIONS = {
    "default": "Thresholds as documented in THREATS.md.",
    "resume": (
        "Resume screening: hidden data is high, any ActualText is a finding, "
        "hiring phrases count as instructions."
    ),
    "peer-review": (
        "Manuscript review: ligature ActualText and long figure alt text are expected; "
        "review phrases count as instructions."
    ),
    "rag-ingest": (
        "Documents entering an index: OCR layers on scans are expected; "
        "phrases addressed to the assistant count as instructions."
    ),
}


@router.get("", response_model=ProfileList)
def list_profiles() -> ProfileList:
    return ProfileList(
        profiles=[
            ProfileOut(
                name=name,
                version=load_profile(name).version,
                description=DESCRIPTIONS.get(name, ""),
            )
            for name in profile_names()
        ]
    )
