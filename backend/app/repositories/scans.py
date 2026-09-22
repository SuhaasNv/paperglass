"""Scans: create, read by id, list by session, purge expired."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models import Scan


class ScanRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, scan: Scan) -> Scan:
        self.session.add(scan)
        self.session.commit()
        return scan

    def get(self, scan_id: str) -> Scan | None:
        scan = self.session.get(Scan, scan_id)
        if scan is None or scan.expires_at <= datetime.now(UTC).replace(
            tzinfo=scan.expires_at.tzinfo
        ):
            return None
        return scan

    def list_for_session(self, session_id: str, limit: int = 100) -> list[Scan]:
        now = datetime.now(UTC)
        statement = (
            select(Scan)
            .where(Scan.session_id == session_id, Scan.expires_at > now)
            .order_by(Scan.created_at.desc())
            .limit(limit)
        )
        return list(self.session.scalars(statement))

    def save(self, scan: Scan) -> Scan:
        self.session.add(scan)
        self.session.commit()
        return scan

    def purge_expired(self) -> int:
        expired = list(
            self.session.scalars(select(Scan.id).where(Scan.expires_at <= datetime.now(UTC)))
        )
        if expired:
            self.session.execute(delete(Scan).where(Scan.id.in_(expired)))
        self.session.commit()
        return len(expired)
