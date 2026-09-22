"""Run a parser call in a child process with CPU, memory and wall-clock limits.

The child never gets the network (parsers do not import a client; the layering test proves
it) and never gets more than the budget. Any crash, timeout or limit hit comes back as a
ParseFailure; the caller never sees an exception from a parser.

POSIX applies RLIMIT_CPU and RLIMIT_AS in the child. On macOS RLIMIT_AS is advisory for
some allocators, so the wall clock is the limit that always holds. Windows has no
resource module; the wall clock is enforced and CPU and memory caps are documented as
best effort until a job-object implementation lands (tracked in SANDBOX.md).
"""

from __future__ import annotations

import contextlib
import multiprocessing as mp
import sys
import traceback
from collections.abc import Callable
from dataclasses import dataclass
from multiprocessing.connection import Connection
from typing import Final, Generic, TypeVar

from paperglass.ingest.limits import Limits
from paperglass.models import ParseFailure

R = TypeVar("R")

_CONTEXT: Final = mp.get_context("spawn")
_GRACE_SECONDS: Final = 0.5


@dataclass(frozen=True)
class SandboxResult(Generic[R]):
    """Either a value or a failure, never both."""

    value: R | None
    failure: ParseFailure | None

    @property
    def ok(self) -> bool:
        return self.failure is None


def _apply_rlimits(limits: Limits) -> None:
    if sys.platform == "win32":
        return
    import resource  # noqa: PLC0415  # POSIX only; importing at module level breaks Windows

    cpu = limits.cpu_seconds
    resource.setrlimit(resource.RLIMIT_CPU, (cpu, cpu + 1))
    memory = limits.memory_mb * 1024 * 1024
    # Some platforms refuse to lower RLIMIT_AS; the wall clock still bounds the call.
    with contextlib.suppress(ValueError, OSError):
        resource.setrlimit(resource.RLIMIT_AS, (memory, memory))


def _child(
    connection: Connection,
    limits: Limits,
    func: Callable[..., object],
    args: tuple[object, ...],
    kwargs: dict[str, object],
) -> None:  # pragma: no cover - runs in the child process
    _apply_rlimits(limits)
    try:
        result = func(*args, **kwargs)
    except MemoryError:
        connection.send(("failure", "memory", "MemoryError"))
    except BaseException as exc:  # noqa: BLE001  # the whole point: nothing escapes the sandbox
        connection.send(("failure", "crash", f"{type(exc).__name__}: {exc}"[:500]))
        traceback.clear_frames(exc.__traceback__)
    else:
        connection.send(("value", result))
    finally:
        connection.close()


def run_sandboxed(  # noqa: PLR0913  # func, args, kwargs plus three named budgets
    func: Callable[..., R],
    args: tuple[object, ...] = (),
    kwargs: dict[str, object] | None = None,
    *,
    limits: Limits,
    parser: str,
    stage: int = 0,
) -> SandboxResult[R]:
    """Call func(*args, **kwargs) in a spawned child under the limits.

    func must be importable by name (module level) because the child is spawned, and its
    arguments and return value must be picklable.
    """
    from paperglass.ingest import pool as _pool  # noqa: PLC0415  # avoids an import cycle

    if _pool.pool_enabled():
        result = _pool.get_pool(limits).call(
            func, args, kwargs, limits=limits, parser=parser, stage=stage
        )
        return SandboxResult(value=result.value, failure=result.failure)  # type: ignore[arg-type]  # R is func's return

    parent, child = _CONTEXT.Pipe(duplex=False)
    process = _CONTEXT.Process(
        target=_child,
        args=(child, limits, func, args, dict(kwargs or {})),
        daemon=True,
    )
    process.start()
    child.close()
    try:
        if not parent.poll(limits.wall_seconds):
            _kill(process)
            return SandboxResult(
                value=None,
                failure=ParseFailure(
                    stage=stage,
                    parser=parser,
                    reason="timeout",
                    message=f"no result within {limits.wall_seconds} s",
                ),
            )
        message = parent.recv()
    except (EOFError, OSError):
        _kill(process)
        return SandboxResult(
            value=None,
            failure=_failure_from_exit(process.exitcode, parser=parser, stage=stage),
        )
    finally:
        parent.close()
        process.join(_GRACE_SECONDS)
        if process.is_alive():
            _kill(process)
    kind = message[0]
    if kind == "value":
        return SandboxResult(value=message[1], failure=None)
    _, reason, text = message
    return SandboxResult(
        value=None,
        failure=ParseFailure(stage=stage, parser=parser, reason=reason, message=text),
    )


def _kill(process: mp.process.BaseProcess) -> None:
    if process.is_alive():
        process.terminate()
        process.join(_GRACE_SECONDS)
    if process.is_alive():
        process.kill()
        process.join(_GRACE_SECONDS)


def _failure_from_exit(exitcode: int | None, *, parser: str, stage: int) -> ParseFailure:
    """A child that died without sending: the CPU limit, out of memory, or a native crash."""
    if exitcode is not None and exitcode < 0:
        signal_number = -exitcode
        if signal_number in (24, 30):  # SIGXCPU, SIGUSR1 on some libcs
            return ParseFailure(
                stage=stage, parser=parser, reason="cpu", message=f"signal {signal_number}"
            )
        if signal_number == 9:  # SIGKILL: the memory limit or the OS
            return ParseFailure(stage=stage, parser=parser, reason="memory", message="killed")
        return ParseFailure(
            stage=stage, parser=parser, reason="crash", message=f"signal {signal_number}"
        )
    return ParseFailure(stage=stage, parser=parser, reason="crash", message=f"exit code {exitcode}")
