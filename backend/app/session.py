"""An anonymous, signed, httpOnly session cookie: a browser's history, no account."""

from __future__ import annotations

import secrets

from fastapi import Request, Response
from itsdangerous import BadSignature, URLSafeSerializer

COOKIE = "pg_session"
MAX_AGE = 60 * 60 * 24 * 30


def _serializer(secret: str) -> URLSafeSerializer:
    return URLSafeSerializer(secret, salt="paperglass-session")


def read_session(request: Request, secret: str) -> str | None:
    raw = request.cookies.get(COOKIE)
    if not raw:
        return None
    try:
        value = _serializer(secret).loads(raw)
    except BadSignature:
        return None
    return str(value) if isinstance(value, str) and len(value) >= 16 else None


def ensure_session(request: Request, response: Response, secret: str, *, secure: bool) -> str:
    """Return the session id, setting a fresh cookie when the request has none."""
    existing = read_session(request, secret)
    if existing is not None:
        return existing
    session_id = secrets.token_urlsafe(24)
    response.set_cookie(
        COOKIE,
        _serializer(secret).dumps(session_id),
        max_age=MAX_AGE,
        httponly=True,
        samesite="lax",
        secure=secure,
        path="/",
    )
    return session_id
