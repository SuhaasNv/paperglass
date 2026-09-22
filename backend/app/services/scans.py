"""Scan an upload in memory, store the report, never the file."""

from __future__ import annotations

import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.models import Scan
from app.repositories.scans import ScanRepository
from paperglass.engine import fingerprint_bytes, scan_bytes
from paperglass.models import Fingerprint, Report, Tier


class UploadTooLargeError(Exception):
    def __init__(self, size: int, limit_mb: int) -> None:
        super().__init__(f"{size} bytes exceeds the {limit_mb} MB limit")
        self.size = size
        self.limit_mb = limit_mb


def new_id() -> str:
    """22 URL-safe characters (about 131 bits): the share link is the secret."""
    return secrets.token_urlsafe(16)


class ScanService:
    def __init__(self, session: Session, *, retention_days: int, max_upload_mb: int) -> None:
        self.repository = ScanRepository(session)
        self.retention = timedelta(days=retention_days)
        self.max_upload = max_upload_mb * 1024 * 1024
        self.limit_mb = max_upload_mb

    def create(
        self, data: bytes, *, file_name: str, session_id: str, tier: Tier, profile: str
    ) -> Scan:
        if len(data) > self.max_upload:
            raise UploadTooLargeError(len(data), self.limit_mb)
        report = scan_bytes(data, tier=tier, profile=profile)
        now = datetime.now(UTC)
        scan = Scan(
            id=new_id(),
            session_id=session_id,
            created_at=now,
            expires_at=now + self.retention,
            file_name=file_name[:255],
            input_sha256=report.input_sha256,
            input_type=report.input_type,
            verdict=report.verdict.value,
            tier=report.tier.value,
            profile=report.profile,
            report_json=report.model_dump(mode="json"),
            fingerprint_json=None,
            tool_version=report.tool_version,
        )
        return self.repository.add(scan)

    def get(self, scan_id: str) -> Scan | None:
        return self.repository.get(scan_id)

    def list_for_session(self, session_id: str) -> list[Scan]:
        return self.repository.list_for_session(session_id)

    def fingerprint(self, scan: Scan, data: bytes | None) -> Fingerprint | None:
        """The fingerprint needs the bytes; the file is not stored, so the client re-sends it.

        Returns the cached fingerprint when one exists, else runs it when bytes are given.
        """
        if scan.fingerprint_json is not None:
            return Fingerprint.model_validate(scan.fingerprint_json)
        if data is None:
            return None
        report = Report.model_validate(scan.report_json)
        if report.input_sha256 != _sha256(data):
            return None
        result = fingerprint_bytes(data, report=report)
        scan.fingerprint_json = result.model_dump(mode="json")
        self.repository.save(scan)
        return result

    def purge_expired(self) -> int:
        return self.repository.purge_expired()


def _sha256(data: bytes) -> str:
    from paperglass.models import sha256_of  # noqa: PLC0415  # keeps the import surface small

    return sha256_of(data)
