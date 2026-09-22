"""The FastAPI application: routers, error shape, request ids, CORS, retention sweep."""

from __future__ import annotations

import asyncio
import contextlib
import logging
import uuid
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, profiles, scans, techniques
from app.db import get_engine, get_session
from app.errors import install_error_handlers
from app.models import Base
from app.services.scans import ScanService
from app.settings import get_settings

log = logging.getLogger("paperglass.backend")


def purge_once() -> int:
    """Delete every scan past its expiry. Runs at startup and on the sweep interval."""
    settings = get_settings()
    purged = 0
    for session in get_session():
        purged = ScanService(
            session, retention_days=settings.retention_days, max_upload_mb=settings.max_upload_mb
        ).purge_expired()
    if purged:
        log.info("purged %d expired scans", purged)
    return purged


async def purge_forever(interval_seconds: float) -> None:
    """The retention sweep: the 7-day promise holds on a process that never restarts."""
    while True:
        await asyncio.sleep(interval_seconds)
        try:
            await asyncio.to_thread(purge_once)
        except Exception:  # a failed sweep is logged, never fatal
            log.exception("retention sweep failed")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    settings.validate_for_startup()
    if settings.database_url.startswith("sqlite"):
        Base.metadata.create_all(get_engine())  # tests and local play; Postgres uses Alembic
    purge_once()
    sweep = asyncio.create_task(purge_forever(settings.purge_interval_minutes * 60))
    app.state.purge_task = sweep
    try:
        yield
    finally:
        sweep.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await sweep


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Paperglass",
        version="0.2.0",
        description="See exactly what the model reads.",
        lifespan=lifespan,
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_list,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def request_id(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        rid = request.headers.get("x-request-id") or uuid.uuid4().hex[:16]
        response = await call_next(request)
        response.headers["x-request-id"] = rid
        log.info("%s %s %s rid=%s", request.method, request.url.path, response.status_code, rid)
        return response

    install_error_handlers(app)
    app.include_router(health.router)
    app.include_router(scans.router)
    app.include_router(techniques.router)
    app.include_router(profiles.router)
    return app


app = create_app()


def run() -> None:  # pragma: no cover - entry point
    import uvicorn  # noqa: PLC0415

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, log_level=get_settings().log_level)  # noqa: S104  # container entry point
