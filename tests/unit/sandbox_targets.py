"""Module-level callables for the sandbox tests (a spawned child imports them by name)."""

from __future__ import annotations

import time


def add(a: int, b: int) -> int:
    return a + b


def sleep_forever() -> None:
    time.sleep(60)


def raise_value_error() -> None:
    msg = "bad input"
    raise ValueError(msg)


def burn_cpu() -> int:
    total = 0
    while True:
        total += 1


def allocate(megabytes: int) -> int:
    block = bytearray(megabytes * 1024 * 1024)
    return len(block)
