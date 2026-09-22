"""SQLAlchemy 2 engine and session. PostgreSQL in every environment; SQLite for unit tests."""

from __future__ import annotations

from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.settings import get_settings


def normalise_url(url: str) -> str:
    """Platforms hand out postgres:// or postgresql:// URLs; the driver here is pg8000."""
    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            return "postgresql+pg8000://" + url[len(prefix) :]
    return url


def make_engine(url: str) -> Engine:
    url = normalise_url(url)
    if url.startswith("sqlite"):
        return create_engine(
            url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool if ":memory:" in url else None,
        )
    return create_engine(url, pool_pre_ping=True)


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    return make_engine(get_settings().database_url)


def get_session() -> Iterator[Session]:
    factory = sessionmaker(bind=get_engine(), expire_on_commit=False)
    with factory() as session:
        yield session
