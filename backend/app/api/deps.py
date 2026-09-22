"""Request-scoped dependencies: settings, database session, browser session."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, Request, Response
from sqlalchemy.orm import Session

from app.db import get_session
from app.services.scans import ScanService
from app.session import ensure_session
from app.settings import Settings, get_settings

SettingsDep = Annotated[Settings, Depends(get_settings)]


def db_session() -> Iterator[Session]:
    yield from get_session()


DbDep = Annotated[Session, Depends(db_session)]


def browser_session(request: Request, response: Response, settings: SettingsDep) -> str:
    return ensure_session(
        request, response, settings.session_secret, secure=settings.env != "development"
    )


BrowserSessionDep = Annotated[str, Depends(browser_session)]


def scan_service(db: DbDep, settings: SettingsDep) -> ScanService:
    return ScanService(
        db, retention_days=settings.retention_days, max_upload_mb=settings.max_upload_mb
    )


ScanServiceDep = Annotated[ScanService, Depends(scan_service)]
