"""The scans API: upload in memory, stored report, session-scoped history, error shape."""

from __future__ import annotations

import pathlib

from fastapi import FastAPI
from fastapi.testclient import TestClient

from paperglass.redkit.minipdf import simple

ROOT = pathlib.Path(__file__).resolve().parents[2]
POSITIVE = ROOT / "tests/fixtures/pdf/pdf.text.low_contrast/positive.pdf"


def upload(
    client: TestClient, data: bytes, name: str = "resume.pdf", **form: str
) -> dict[str, object]:
    response = client.post(
        "/api/v1/scans",
        files={"file": (name, data, "application/pdf")},
        data={"tier": "fast", **form},
    )
    assert response.status_code == 201, response.text
    body: dict[str, object] = response.json()
    return body


def test_upload_returns_the_report_and_sets_a_session_cookie(client: TestClient) -> None:
    body = upload(client, POSITIVE.read_bytes())
    assert body["verdict"] == "malicious"
    assert body["file_name"] == "resume.pdf"
    report = body["report"]
    assert isinstance(report, dict) and report["schema_version"] == 2
    assert "pg_session" in client.cookies
    assert len(str(body["id"])) >= 20


def test_history_is_scoped_to_the_browser_session(client: TestClient) -> None:
    upload(client, simple("Hello"), name="a.pdf")
    upload(client, simple("World"), name="b.pdf")
    listed = client.get("/api/v1/scans").json()["scans"]
    assert [s["file_name"] for s in listed] == ["b.pdf", "a.pdf"]
    other = TestClient(client.app, base_url="https://testserver")
    assert other.get("/api/v1/scans").json()["scans"] == []


def test_get_by_id_and_unknown_id(client: TestClient) -> None:
    body = upload(client, simple("Hello"))
    fetched = client.get(f"/api/v1/scans/{body['id']}")
    assert fetched.status_code == 200 and fetched.json()["id"] == body["id"]
    missing = client.get("/api/v1/scans/does-not-exist")
    assert missing.status_code == 404
    assert missing.json() == {
        "error": {"code": "not_found", "message": "scan not found or expired"}
    }


def test_share_link_works_without_the_cookie(client: TestClient) -> None:
    body = upload(client, simple("Hello"))
    stranger = TestClient(client.app, base_url="https://testserver")
    assert stranger.get(f"/api/v1/scans/{body['id']}").status_code == 200


def test_bad_tier_and_bad_profile_are_422_in_the_standard_shape(client: TestClient) -> None:
    response = client.post(
        "/api/v1/scans",
        files={"file": ("x.pdf", simple("x"), "application/pdf")},
        data={"tier": "warp"},
    )
    assert response.status_code == 422 and response.json()["error"]["code"] == "validation_error"
    response = client.post(
        "/api/v1/scans",
        files={"file": ("x.pdf", simple("x"), "application/pdf")},
        data={"tier": "fast", "profile": "nope"},
    )
    assert response.status_code == 422


def test_too_large_is_413(client: TestClient, monkeypatch: object) -> None:
    from app.settings import get_settings  # noqa: PLC0415

    settings = get_settings()
    original = settings.max_upload_mb
    object.__setattr__(settings, "max_upload_mb", 1)
    try:
        response = client.post(
            "/api/v1/scans",
            files={"file": ("big.pdf", b"%PDF-1.7" + b"x" * (1024 * 1024 + 10), "application/pdf")},
            data={"tier": "fast"},
        )
    finally:
        object.__setattr__(settings, "max_upload_mb", original)
    assert response.status_code == 413
    assert response.json()["error"]["code"] == "too_large"


def test_fingerprint_needs_the_same_file_again(client: TestClient) -> None:
    data = POSITIVE.read_bytes()
    body = upload(client, data)
    without = client.post(f"/api/v1/scans/{body['id']}/fingerprint")
    assert without.status_code == 409
    wrong = client.post(
        f"/api/v1/scans/{body['id']}/fingerprint",
        files={"file": ("other.pdf", simple("other"), "application/pdf")},
    )
    assert wrong.status_code == 409
    right = client.post(
        f"/api/v1/scans/{body['id']}/fingerprint",
        files={"file": ("resume.pdf", data, "application/pdf")},
    )
    assert right.status_code == 200
    fingerprint = right.json()["fingerprint"]
    assert fingerprint["rows"][0]["technique_id"] == "pdf.text.low_contrast"
    cached = client.post(f"/api/v1/scans/{body['id']}/fingerprint")
    assert cached.status_code == 200 and cached.json()["fingerprint"] == fingerprint


def test_techniques_and_health_and_request_id(client: TestClient) -> None:
    techniques = client.get("/api/v1/techniques")
    assert techniques.status_code == 200
    ids = [t["id"] for t in techniques.json()["techniques"]]
    assert "pdf.render.mode" in ids and ids == sorted(ids)
    health = client.get("/healthz", headers={"x-request-id": "abc123"})
    assert health.status_code == 200 and health.json()["database"] == "ok"
    assert health.headers["x-request-id"] == "abc123"


def test_expired_scans_are_invisible_and_purged(client: TestClient) -> None:
    from datetime import UTC, datetime, timedelta  # noqa: PLC0415

    from app.db import get_session  # noqa: PLC0415
    from app.models import Scan  # noqa: PLC0415
    from app.repositories.scans import ScanRepository  # noqa: PLC0415

    body = upload(client, simple("Hello"))
    for session in get_session():
        scan = session.get(Scan, body["id"])
        assert scan is not None
        scan.expires_at = datetime.now(UTC) - timedelta(seconds=1)
        session.commit()
        assert client.get(f"/api/v1/scans/{body['id']}").status_code == 404
        assert ScanRepository(session).purge_expired() == 1


def test_profiles_are_listed_with_a_sentence_each(client: TestClient) -> None:
    body = client.get("/api/v1/profiles").json()
    names = [p["name"] for p in body["profiles"]]
    assert names == ["default", "peer-review", "rag-ingest", "resume"]
    assert all(p["description"] for p in body["profiles"])
    scan = upload(client, simple("Hello"), name="a.pdf", profile="resume")
    assert scan["profile"] == "resume"
    report = scan["report"]
    assert isinstance(report, dict) and report["profile"] == "resume"
    refused = client.post(
        "/api/v1/scans",
        files={"file": ("a.pdf", simple("Hello"), "application/pdf")},
        data={"profile": "nope"},
    )
    assert refused.status_code == 422


def test_platform_database_urls_are_routed_to_pg8000() -> None:
    from app.db import normalise_url  # noqa: PLC0415

    assert normalise_url("postgres://u:p@h:5432/d") == "postgresql+pg8000://u:p@h:5432/d"
    assert normalise_url("postgresql://u:p@h/d") == "postgresql+pg8000://u:p@h/d"
    assert normalise_url("postgresql+pg8000://u:p@h/d") == "postgresql+pg8000://u:p@h/d"
    assert normalise_url("sqlite+pysqlite:///:memory:") == "sqlite+pysqlite:///:memory:"


def test_html_report_download(client: TestClient) -> None:
    scan = upload(client, simple("Hello"), name="a.pdf")
    response = client.get(f"/api/v1/scans/{scan['id']}/report.html")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert response.headers["content-disposition"] == 'attachment; filename="a.paperglass.html"'
    assert response.text.startswith("<!doctype html>") and "CLEAN" in response.text
    assert client.get("/api/v1/scans/nope/report.html").status_code == 404


def test_the_retention_sweep_runs_without_a_restart(client: TestClient) -> None:
    from datetime import UTC, datetime, timedelta  # noqa: PLC0415

    from app.db import get_session  # noqa: PLC0415
    from app.main import purge_once  # noqa: PLC0415
    from app.models import Scan  # noqa: PLC0415

    scan = upload(client, simple("Hello"), name="a.pdf")
    for session in get_session():
        row = session.get(Scan, scan["id"])
        assert row is not None
        row.expires_at = datetime.now(UTC) - timedelta(days=1)
        session.commit()
    app = client.app
    assert isinstance(app, FastAPI)
    assert app.state.purge_task is not None and not app.state.purge_task.done()
    assert purge_once() == 1
    for session in get_session():
        assert session.get(Scan, scan["id"]) is None
