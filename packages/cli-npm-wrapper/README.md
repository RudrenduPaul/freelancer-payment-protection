# freelancer-payment-protection-cli (npm wrapper)

An `npx`-installable wrapper around the real [freelancer-payment-protection CLI](https://github.com/RudrenduPaul/freelancer-payment-protection/tree/main/packages/cli), which is a Python program that talks to the project's FastAPI backend and to Supabase directly.

![Login and first command](https://raw.githubusercontent.com/RudrenduPaul/freelancer-payment-protection/main/docs/demo.gif)

This package does not reimplement the CLI in Node. Every invocation shells out to `uvx`/`pipx`, pinned to this wrapper's own version so the npm and PyPI releases stay in lockstep. It exists so Node-first tooling and agent sandboxes that reach for `npx <name>-cli` get the same CLI without installing it manually from PyPI first.

## Requirements

`uv` or `pipx` must be on `PATH` so this wrapper can bootstrap the real Python CLI. If neither is found, it prints an install link and exits with a nonzero status rather than failing silently.

## Install

```bash
npm install -g freelancer-payment-protection-cli
# or run without installing:
npx freelancer-payment-protection-cli --help
```

## Usage

```bash
fpp login
fpp invoice list --status overdue --json
fpp client risk <client-id>
```

![Filtering invoices, scoring a client, and checking escalation status](https://raw.githubusercontent.com/RudrenduPaul/freelancer-payment-protection/main/docs/usage.gif)

See the [main README](https://github.com/RudrenduPaul/freelancer-payment-protection#readme) or the [full CLI documentation](https://github.com/RudrenduPaul/freelancer-payment-protection/tree/main/packages/cli#readme) for the complete command reference, login/auth walkthrough, and FAQ.

## License

Proprietary. See [LICENSE](https://github.com/RudrenduPaul/freelancer-payment-protection/blob/main/LICENSE) in the parent repository for full terms.
