"""One error shape everywhere: { "error": { "code", "message", "details"? } }."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

CODES = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    413: "too_large",
    415: "unsupported_type",
    422: "validation_error",
    429: "rate_limited",
    500: "internal_error",
}


def error_response(
    status: int, message: str, details: object = None, code: str | None = None
) -> JSONResponse:
    body: dict[str, object] = {"code": code or CODES.get(status, "error"), "message": message}
    if details is not None:
        body["details"] = details
    return JSONResponse(status_code=status, content={"error": body})


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def _http(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        detail = exc.detail if isinstance(exc.detail, str) else "request failed"
        return error_response(exc.status_code, detail)

    @app.exception_handler(RequestValidationError)
    async def _validation(_: Request, exc: RequestValidationError) -> JSONResponse:
        return error_response(422, "validation failed", details=exc.errors())

    @app.exception_handler(Exception)
    async def _unhandled(_: Request, __: Exception) -> JSONResponse:
        return error_response(500, "internal error")
