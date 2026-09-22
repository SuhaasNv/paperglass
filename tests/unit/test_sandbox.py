"""The sandbox turns every failure into a ParseFailure and never raises to the caller."""

from __future__ import annotations

import sys

import pytest

from paperglass.ingest import Limits, run_sandboxed
from paperglass.ingest.pool import SandboxPool
from tests.unit import sandbox_targets as targets

FAST = Limits(wall_seconds=2.0, cpu_seconds=1, memory_mb=256)


def test_value_comes_back() -> None:
    result = run_sandboxed(targets.add, (2, 3), limits=FAST, parser="test")
    assert result.ok
    assert result.value == 5


def test_timeout_is_a_failure_not_an_exception() -> None:
    result = run_sandboxed(targets.sleep_forever, limits=Limits(wall_seconds=0.5), parser="test")
    assert not result.ok
    assert result.failure is not None
    assert result.failure.reason == "timeout"
    assert result.failure.parser == "test"


def test_exception_is_a_crash_failure() -> None:
    result = run_sandboxed(targets.raise_value_error, limits=FAST, parser="test", stage=2)
    assert result.failure is not None
    assert result.failure.reason == "crash"
    assert "ValueError" in result.failure.message
    assert result.failure.stage == 2


@pytest.mark.skipif(sys.platform == "win32", reason="RLIMIT_CPU is POSIX only")
def test_cpu_limit_kills_a_busy_loop() -> None:
    result = run_sandboxed(
        targets.burn_cpu, limits=Limits(wall_seconds=10, cpu_seconds=1), parser="test"
    )
    assert result.failure is not None
    assert result.failure.reason in {"cpu", "timeout", "crash"}


@pytest.mark.skipif(sys.platform != "linux", reason="RLIMIT_AS is reliable on Linux only")
def test_memory_limit_is_reported() -> None:
    result = run_sandboxed(targets.allocate, (1024,), limits=Limits(memory_mb=128), parser="test")
    assert result.failure is not None
    assert result.failure.reason in {"memory", "crash"}


def test_pool_reuses_one_worker_and_survives_a_timeout() -> None:
    pool = SandboxPool(FAST)
    try:
        first = pool.call(targets.add, (1, 2), limits=FAST, parser="test")
        assert first.value == 3
        pid = pool._process.pid if pool._process else None  # test peeks
        second = pool.call(targets.add, (2, 2), limits=FAST, parser="test")
        assert second.value == 4
        assert pool._process is not None and pool._process.pid == pid
        timed_out = pool.call(targets.sleep_forever, limits=Limits(wall_seconds=0.5), parser="test")
        assert timed_out.failure is not None and timed_out.failure.reason == "timeout"
        third = pool.call(targets.add, (5, 5), limits=FAST, parser="test")
        assert third.value == 10
        assert pool._process is not None and pool._process.pid != pid
        crashed = pool.call(targets.raise_value_error, limits=FAST, parser="test")
        assert crashed.failure is not None and crashed.failure.reason == "crash"
    finally:
        pool.close()


def test_run_sandboxed_without_the_pool(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PAPERGLASS_SANDBOX_POOL", "0")
    result = run_sandboxed(targets.add, (4, 5), limits=FAST, parser="test")
    assert result.value == 9
    timed_out = run_sandboxed(targets.sleep_forever, limits=Limits(wall_seconds=0.5), parser="test")
    assert timed_out.failure is not None and timed_out.failure.reason == "timeout"
