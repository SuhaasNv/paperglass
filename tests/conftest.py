"""Session-wide fixtures."""

from __future__ import annotations

from collections.abc import Iterator

import pytest

from paperglass.ingest import close_pool


@pytest.fixture(autouse=True, scope="session")
def _close_sandbox_pool() -> Iterator[None]:
    """Stop the sandbox worker cleanly so its coverage data lands before pytest-cov combines."""
    yield
    close_pool()
