"""GET /healthz: the process and the database; never provider details."""

from __future__ import annotations

from fastapi import APIRouter, Response
from sqlalchemy import text

from app.api.deps import DbDep
from paperglass import __version__

router = APIRouter(tags=["health"])


@router.get("/healthz")
def healthz(db: DbDep, response: Response) -> dict[str, str]:
    try:
        db.execute(text("SELECT 1"))
        database = "ok"
    except Exception:  # noqa: BLE001  # any database error is a 503, not a stack trace
        database = "unavailable"
        response.status_code = 503
    return {
        "status": "ok" if database == "ok" else "degraded",
        "database": database,
        "version": __version__,
    }
