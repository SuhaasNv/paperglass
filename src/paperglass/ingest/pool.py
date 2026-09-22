"""A long-lived sandbox worker so a scan does not pay an interpreter start per parser call.

One spawned child handles calls one after another; the parent enforces the wall clock per
call and kills and respawns the worker on a timeout, a crash or after a fixed number of
calls (so memory from one document does not linger). The memory limit is applied at
worker start; the CPU limit is enforced through the wall clock (RLIMIT_CPU is cumulative
over a process's life and cannot be reset per call). docs/03-architecture/SANDBOX.md.
"""

from __future__ import annotations

import atexit
import contextlib
import importlib
import multiprocessing as mp
import os
import threading
from collections.abc import Callable
from multiprocessing.connection import Connection
from typing import Final

from paperglass.ingest.limits import Limits
from paperglass.ingest.sandbox import SandboxResult, _apply_rlimits, _failure_from_exit, _kill
from paperglass.models import ParseFailure

_CONTEXT: Final = mp.get_context("spawn")
_CALLS_PER_WORKER: Final = 200
_GRACE: Final = 0.5


def _worker_loop(connection: Connection, limits: Limits) -> None:  # pragma: no cover - child
    _apply_rlimits(limits.model_copy(update={"cpu_seconds": 10**6}))
    while True:
        try:
            message = connection.recv()
        except (EOFError, OSError):
            return
        if message is None:
            return
        module_name, qualname, args, kwargs = message
        try:
            target: object = importlib.import_module(module_name)
            for part in qualname.split("."):
                target = getattr(target, part)
            func: Callable[..., object] = target  # type: ignore[assignment]  # resolved by name
            result = func(*args, **kwargs)
        except MemoryError:
            connection.send(("failure", "memory", "MemoryError"))
        except BaseException as exc:  # noqa: BLE001  # nothing escapes the sandbox
            connection.send(("failure", "crash", f"{type(exc).__name__}: {exc}"[:500]))
        else:
            connection.send(("value", result))


class SandboxPool:
    """One worker, reused; thread-safe; transparent respawn."""

    def __init__(self, limits: Limits) -> None:
        self._limits = limits
        self._lock = threading.Lock()
        self._process: mp.process.BaseProcess | None = None
        self._connection: Connection | None = None
        self._calls = 0

    def _start(self) -> None:
        parent, child = _CONTEXT.Pipe(duplex=True)
        process = _CONTEXT.Process(target=_worker_loop, args=(child, self._limits), daemon=True)
        process.start()
        child.close()
        self._process, self._connection, self._calls = process, parent, 0

    def _stop(self) -> None:
        """Ask the worker to exit, wait briefly, then kill. A clean exit lets it flush."""
        if self._connection is not None:
            with contextlib.suppress(OSError, ValueError):
                self._connection.send(None)
            self._connection.close()
        if self._process is not None:
            self._process.join(_GRACE)
            _kill(self._process)
        self._process, self._connection = None, None

    def close(self) -> None:
        with self._lock:
            self._stop()

    def call(  # noqa: PLR0913  # mirrors run_sandboxed
        self,
        func: Callable[..., object],
        args: tuple[object, ...] = (),
        kwargs: dict[str, object] | None = None,
        *,
        limits: Limits,
        parser: str,
        stage: int = 0,
    ) -> SandboxResult[object]:
        with self._lock:
            if (
                self._process is None
                or not self._process.is_alive()
                or self._calls >= _CALLS_PER_WORKER
            ):
                self._stop()
                self._start()
            assert self._connection is not None and self._process is not None
            self._calls += 1
            try:
                self._connection.send(
                    (func.__module__, func.__qualname__, args, dict(kwargs or {}))
                )
                if not self._connection.poll(limits.wall_seconds):
                    self._stop()
                    return SandboxResult(
                        value=None,
                        failure=ParseFailure(
                            stage=stage,
                            parser=parser,
                            reason="timeout",
                            message=f"no result within {limits.wall_seconds} s",
                        ),
                    )
                message = self._connection.recv()
            except (EOFError, OSError, ValueError):
                exitcode = self._process.exitcode
                self._stop()
                return SandboxResult(
                    value=None, failure=_failure_from_exit(exitcode, parser=parser, stage=stage)
                )
        if message[0] == "value":
            return SandboxResult(value=message[1], failure=None)
        _, reason, text = message
        return SandboxResult(
            value=None,
            failure=ParseFailure(stage=stage, parser=parser, reason=reason, message=text),
        )


_POOL: SandboxPool | None = None
_POOL_LOCK = threading.Lock()


def pool_enabled() -> bool:
    return os.environ.get("PAPERGLASS_SANDBOX_POOL", "1") != "0"


def get_pool(limits: Limits) -> SandboxPool:
    global _POOL  # noqa: PLW0603  # one worker per process is the point
    with _POOL_LOCK:
        if _POOL is None:
            _POOL = SandboxPool(limits)
            atexit.register(close_pool)
        return _POOL


def close_pool() -> None:
    global _POOL  # noqa: PLW0603
    with _POOL_LOCK:
        if _POOL is not None:
            _POOL.close()
            _POOL = None
