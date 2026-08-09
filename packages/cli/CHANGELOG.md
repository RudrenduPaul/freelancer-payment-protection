# Changelog

All notable changes to `freelancer-payment-protection-cli` (the PyPI package
in `packages/cli/`) are documented here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.1.5] - 2026-08-08

### Fixed

- `fpp --version` / `freelancer-payment-protection --version` reported
  `0.1.0` on every release since the package's first publish, regardless
  of which version was actually installed (confirmed on PyPI's published
  0.1.4 build via a clean `pip install` — `pip show` correctly reported
  `0.1.4` while `fpp --version` still printed `0.1.0`). Root cause:
  `src/freelancer_payment_protection_cli/__init__.py`'s `__version__`
  constant was set once at the initial commit and never updated in
  lockstep with `pyproject.toml`'s `[project.version]` across the
  0.1.1-0.1.4 releases. Fixed by making `__init__.py` the single source
  of truth: `pyproject.toml` now declares `dynamic = ["version"]` with
  `[tool.hatch.version] path = "src/freelancer_payment_protection_cli/__init__.py"`,
  so the build version and the runtime `--version` string can no longer
  drift apart.

## [0.1.0] - [0.1.4]

No changelog was kept for these releases. See git history and PyPI
release history for prior changes.
