#!/usr/bin/env node
'use strict';

const { spawnSync } = require('node:child_process');
const path = require('node:path');

// Pinned to this npm package's own version, not left floating: an unqualified
// "uvx freelancer-payment-protection-cli" / "pipx run freelancer-payment-protection-cli"
// always fetches whatever is currently newest on PyPI. That decouples what a
// user actually installed (this npm package, a fixed point in time) from
// what runs on their machine (PyPI's latest, which changes underneath them).
// Pinning to this package's own version keeps the two registries in
// lockstep: bump this package.json's version when the PyPI package ships a
// new release, and every subsequent invocation resolves to that exact
// pinned release, not whatever is newest at run time.
const PACKAGE_VERSION = require(path.join(__dirname, '..', 'package.json')).version;
const PYPI_PACKAGE = `freelancer-payment-protection-cli==${PACKAGE_VERSION}`;

function commandExists(cmd) {
  const probe = process.platform === 'win32' ? 'where' : 'which';
  const result = spawnSync(probe, [cmd], { stdio: 'ignore' });
  return result.status === 0;
}

function run(cmd, args) {
  const result = spawnSync(cmd, args, { stdio: 'inherit' });
  if (result.error) {
    return null;
  }
  return result.status;
}

const args = process.argv.slice(2);

// freelancer-payment-protection-cli is a Python CLI (it talks to the
// project's FastAPI backend and to Supabase directly). This wrapper never
// bundles a platform binary -- it bootstraps into the real Python CLI via
// whichever Python runner is already on PATH, preferring uv/uvx since
// that's increasingly present by default in agent and CI sandboxes, then
// falling back to pipx.
//
// The PyPI package installs two equivalent console scripts, `fpp` and
// `freelancer-payment-protection` -- since neither matches the package
// name exactly (which ends in `-cli`), both uvx and pipx need to be told
// explicitly which script to run rather than relying on their
// package-name-equals-script-name default.
const runners = [
  { cmd: 'uvx', build: (a) => ['--from', PYPI_PACKAGE, 'fpp', ...a] },
  { cmd: 'pipx', build: (a) => ['run', '--spec', PYPI_PACKAGE, 'fpp', ...a] },
];

for (const runner of runners) {
  if (commandExists(runner.cmd)) {
    const status = run(runner.cmd, runner.build(args));
    if (status !== null) {
      process.exit(status);
    }
  }
}

console.error(
  [
    'freelancer-payment-protection-cli: no Python runner found (checked uvx, pipx).',
    '',
    'This is a Python CLI; this npm package is a thin wrapper that',
    'bootstraps it, not a standalone Node reimplementation.',
    '',
    'Install one of the following, then re-run this command:',
    '  - uv (recommended):  https://docs.astral.sh/uv/getting-started/installation/',
    '  - pipx:              https://pipx.pypa.io/stable/installation/',
    '',
    'Or install the CLI directly with pip:',
    '  pip install freelancer-payment-protection-cli',
  ].join('\n')
);
process.exit(1);
