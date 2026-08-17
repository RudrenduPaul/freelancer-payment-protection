"""MCP server for freelancer-payment-protection-cli.

Exposes a single generic `run` tool that shells out to the installed `fpp`
CLI (see `main.py` / `commands/*.py` for the real command surface) and
returns its output as structured JSON when possible. This is a thin
subprocess wrapper, not a second implementation of the CLI's logic -- every
command the CLI supports (`fpp invoice list`, `fpp client risk <id>`,
`fpp escalation status <id>`, ...) is reachable by passing the same
arguments through this one tool, same as running `fpp <args>` in a shell.

Started via `fpp-mcp` (stdio transport), registered as a console script in
pyproject.toml under the optional `mcp` dependency group.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from typing import Any

from mcp.server import MCPServer

_CLI_BIN = "fpp"
_TIMEOUT_SECONDS = 60

_FALLBACK_DESCRIPTION = (
    "Run the freelancer-payment-protection-cli (`fpp`) with the given "
    "arguments and return its output. Supports every `fpp` subcommand: "
    "login, logout, whoami, invoice (list/create/show/set-status), "
    "escalation (list/status/advance), and client (list/show/risk). Pass "
    "--json on any data-returning command for structured output. Example: "
    'run(args=["invoice", "list", "--status", "overdue", "--json"]).'
)


def _build_tool_description() -> str:
    """Builds the `run` tool description from the CLI's real `--help`
    output at import time, falling back to a static description if that
    subprocess call fails for any reason (binary not on PATH, unexpected
    error, timeout, non-zero exit, empty output, ...). This function must
    never raise -- it runs at module import time.
    """
    try:
        result = subprocess.run(
            [_CLI_BIN, "--help"],
            capture_output=True,
            text=True,
            timeout=_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.TimeoutExpired):
        return _FALLBACK_DESCRIPTION

    if result.returncode != 0 or not result.stdout.strip():
        return _FALLBACK_DESCRIPTION

    return (
        "Run the freelancer-payment-protection-cli (`fpp`) with the given "
        "arguments and return its output as structured JSON when possible. "
        "Pass --json on any data-returning command. Real `fpp --help` "
        f"output:\n\n{result.stdout.strip()}"
    )


server = MCPServer("freelancer-payment-protection-cli")


@server.tool(description=_build_tool_description())
def run(args: list[str]) -> dict[str, Any]:
    """Shell out to `fpp` with `args` and return the result.

    Every failure mode (missing binary, OS error, timeout, non-zero exit,
    unparseable output) is caught and returned as a JSON-serializable dict
    with an "error" key rather than raised -- an MCP tool handler that
    raises breaks the calling agent's tool-call loop.
    """
    if shutil.which(_CLI_BIN) is None:
        return {
            "error": (
                f"'{_CLI_BIN}' not found on PATH. Install it first: "
                "pip install freelancer-payment-protection-cli"
            )
        }

    try:
        result = subprocess.run(
            [_CLI_BIN, *args],
            capture_output=True,
            text=True,
            timeout=_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return {
            "error": f"'{_CLI_BIN} {' '.join(args)}' timed out after {_TIMEOUT_SECONDS}s",
        }
    except OSError as exc:
        return {"error": f"failed to run '{_CLI_BIN}': {exc}"}

    stdout = result.stdout.strip()

    if result.returncode != 0:
        return {
            "error": stdout or result.stderr.strip() or f"'{_CLI_BIN}' exited with status {result.returncode}",
            "returncode": result.returncode,
        }

    if not stdout:
        return {"result": None}

    try:
        return {"result": json.loads(stdout)}
    except json.JSONDecodeError:
        return {"result": stdout}


def main() -> None:
    """Entry point for the `fpp-mcp` console script."""
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
