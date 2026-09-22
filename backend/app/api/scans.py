"""POST and GET /api/v1/scans: the file is scanned in memory and never stored."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import HTMLResponse

from app.api.deps import BrowserSessionDep, ScanServiceDep, SettingsDep
from app.api.schemas import ScanDetail, ScanList, ScanSummary
from app.models import Scan
from app.services.scans import UploadTooLargeError
from paperglass.models import Report, Tier
from paperglass.report import render_html

router = APIRouter(prefix="/api/v1/scans", tags=["scans"])


def _detail(scan: Scan) -> ScanDetail:
    return ScanDetail(
        id=scan.id,
        created_at=scan.created_at,
        expires_at=scan.expires_at,
        file_name=scan.file_name,
        input_type=scan.input_type,
        verdict=scan.verdict,
        tier=scan.tier,
        profile=scan.profile,
        tool_version=scan.tool_version,
        report=scan.report_json,
        fingerprint=scan.fingerprint_json,
    )


@router.post("", response_model=ScanDetail, status_code=201)
async def create_scan(
    service: ScanServiceDep,
    settings: SettingsDep,
    session_id: BrowserSessionDep,
    file: Annotated[UploadFile, File()],
    tier: Annotated[str, Form()] = "standard",
    profile: Annotated[str, Form()] = "default",
) -> ScanDetail:
    try:
        tier_value = Tier(tier)
    except ValueError as exc:
        raise HTTPException(422, f"unknown tier {tier!r}") from exc
    data = await file.read(settings.max_upload_mb * 1024 * 1024 + 1)
    try:
        scan = service.create(
            data,
            file_name=file.filename or "upload",
            session_id=session_id,
            tier=tier_value,
            profile=profile,
        )
    except UploadTooLargeError as exc:
        raise HTTPException(413, str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(422, str(exc.args[0])) from exc
    return _detail(scan)


@router.get("", response_model=ScanList)
def list_scans(service: ScanServiceDep, session_id: BrowserSessionDep) -> ScanList:
    return ScanList(
        scans=[ScanSummary.model_validate(s) for s in service.list_for_session(session_id)]
    )


@router.get("/{scan_id}", response_model=ScanDetail)
def get_scan(scan_id: str, service: ScanServiceDep) -> ScanDetail:
    scan = service.get(scan_id)
    if scan is None:
        raise HTTPException(404, "scan not found or expired")
    return _detail(scan)


@router.get("/{scan_id}/report.html", response_class=HTMLResponse)
def scan_report_html(scan_id: str, service: ScanServiceDep) -> HTMLResponse:
    """The one-file HTML report: opens offline, no external request, same evidence as the page."""
    scan = service.get(scan_id)
    if scan is None:
        raise HTTPException(404, "scan not found or expired")
    html = render_html(Report.model_validate(scan.report_json), file_name=scan.file_name)
    stem = scan.file_name.rsplit(".", 1)[0] or "document"
    safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in stem)[:80]
    return HTMLResponse(
        html,
        headers={"Content-Disposition": f'attachment; filename="{safe}.paperglass.html"'},
    )


@router.post("/{scan_id}/fingerprint", response_model=ScanDetail)
async def fingerprint_scan(
    scan_id: str,
    service: ScanServiceDep,
    settings: SettingsDep,
    file: Annotated[UploadFile | None, File()] = None,
) -> ScanDetail:
    """The file is not stored, so the client sends it again; the result is cached on the scan."""
    scan = service.get(scan_id)
    if scan is None:
        raise HTTPException(404, "scan not found or expired")
    data = await file.read(settings.max_upload_mb * 1024 * 1024 + 1) if file is not None else None
    result = service.fingerprint(scan, data)
    if result is None:
        raise HTTPException(409, "send the same file again to fingerprint it")
    return _detail(scan)
