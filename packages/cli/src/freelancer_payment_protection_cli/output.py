"""Shared output helpers: --json passthrough vs. a plain human-readable table."""
from __future__ import annotations

import json
from contextlib import contextmanager
from typing import Any, Iterator

import click

from .api import ApiError
from .auth import AuthError


@contextmanager
def error_boundary(as_json: bool) -> Iterator[None]:
    """
    Wraps a command body: turns ApiError/AuthError into a clean message
    (JSON-shaped when --json is set) and a non-zero exit, instead of a
    Python traceback.
    """
    try:
        yield
    except ApiError as exc:
        emit_error(exc.detail, as_json, status_code=exc.status_code)
        raise SystemExit(1)
    except AuthError as exc:
        emit_error(str(exc), as_json)
        raise SystemExit(1)


def emit(data: Any, as_json: bool, human: str | None = None) -> None:
    """
    Prints `data` as JSON when --json is set, otherwise prints `human` if
    given, else falls back to a generic key/value dump of `data`.
    """
    if as_json:
        click.echo(json.dumps(data, indent=2, default=str))
        return
    if human is not None:
        click.echo(human)
        return
    click.echo(json.dumps(data, indent=2, default=str))


def emit_error(message: str, as_json: bool, status_code: int | None = None) -> None:
    if as_json:
        payload: dict[str, Any] = {"error": message}
        if status_code is not None:
            payload["status_code"] = status_code
        click.echo(json.dumps(payload, indent=2), err=False)
    else:
        click.echo(f"Error: {message}", err=True)


def kv_table(rows: list[tuple[str, Any]]) -> str:
    width = max((len(k) for k, _ in rows), default=0)
    return "\n".join(f"{k.ljust(width)} : {v}" for k, v in rows)


def simple_table(headers: list[str], rows: list[list[Any]]) -> str:
    if not rows:
        return "(no results)"
    widths = [len(h) for h in headers]
    str_rows = [[str(cell) for cell in row] for row in rows]
    for row in str_rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))
    lines = ["  ".join(h.ljust(widths[i]) for i, h in enumerate(headers))]
    lines.append("  ".join("-" * w for w in widths))
    for row in str_rows:
        lines.append("  ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)))
    return "\n".join(lines)
