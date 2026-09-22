"""An app on an in-memory SQLite database, one per test module."""

from __future__ import annotations

import os
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("PAPERGLASS_DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("APP_ENV", "development")


@pytest.fixture
def client() -> Iterator[TestClient]:
    from app.db import get_engine  # noqa: PLC0415
    from app.main import create_app  # noqa: PLC0415
    from app.models import Base  # noqa: PLC0415

    engine = get_engine()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with TestClient(create_app()) as test_client:
        yield test_client
    Base.metadata.drop_all(engine)
