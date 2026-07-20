# freelancer-payment-protection-cli

Command-line client for [freelancer-payment-protection](https://github.com/RudrenduPaul/freelancer-payment-protection):
automated invoice escalation, legal document generation, and client risk
scoring for freelancers. This package wraps the project's FastAPI backend
(`apps/api/app/routers/*.py`) so the same clients, invoices, escalations,
and risk-scoring data you'd otherwise reach through the dashboard or the
raw HTTP API is scriptable from a terminal or an agent.

![Login and first command](https://raw.githubusercontent.com/RudrenduPaul/freelancer-payment-protection/main/docs/demo.gif)

## Install

```bash
pip install freelancer-payment-protection-cli
```

Or with [uv](https://docs.astral.sh/uv/) / [pipx](https://pipx.pypa.io/):

```bash
uvx freelancer-payment-protection-cli --help
pipx install freelancer-payment-protection-cli
```

Requires Python 3.10+. The console command is installed as both `fpp`
(short form) and `freelancer-payment-protection` (full form) — they are the
same entry point.

## Configuration

The CLI needs to know two things: which backend API to talk to, and which
Supabase project issues your login tokens.

| Variable | Purpose | Default |
|---|---|---|
| `FPP_API_URL` | Backend API base URL | `http://localhost:8000` |
| `FPP_SUPABASE_URL` (or `SUPABASE_URL`) | Your Supabase project URL | none, required for `login` |
| `FPP_SUPABASE_ANON_KEY` (or `SUPABASE_ANON_KEY`) | Your Supabase project's anon key | none, required for `login` |

The anon key is the same public key the web app's Supabase client uses —
it is not a secret, and it's the key already in `apps/web/.env.example` as
`NEXT_PUBLIC_SUPABASE_ANON_KEY`.

## Login and authentication

```bash
export FPP_SUPABASE_URL="https://your-project.supabase.co"
export FPP_SUPABASE_ANON_KEY="your-anon-key"
fpp login
```

`fpp login` prompts for your email and password, then calls Supabase's own
REST auth endpoint directly:

```
POST {SUPABASE_URL}/auth/v1/token?grant_type=password
Header: apikey: <anon key>
Body:   {"email": ..., "password": ...}
```

This is the same call the web dashboard's Supabase client makes — the CLI
never talks to a login endpoint of its own, because the backend
(`apps/api/app/middleware/auth.py`) doesn't mint tokens; it only validates
Supabase-issued JWTs. On success, the returned `access_token` and
`refresh_token` are cached to `~/.config/freelancer-payment-protection-cli/credentials.json`
(mode 600). Every later command reads the JWT's `workspace_id` claim the
same way `get_current_workspace()` does server-side, and transparently
refreshes the access token with the cached refresh token once it expires.

Run `fpp logout` to delete the cached credentials, or `fpp whoami` to see
which workspace and email the cached token resolves to.

## Commands

Every data-returning command supports `--json` for scripting and agent use.

```
fpp login                                   Log in (prompts for email/password)
fpp logout                                  Remove cached credentials
fpp whoami [--json]                         Show cached workspace/session info

fpp invoice list [--status] [--client-id] [--page] [--page-size] [--json]
fpp invoice create --client-id --invoice-number --amount --due-date [...] [--json]
fpp invoice show <invoice-id> [--json]
fpp invoice set-status <invoice-id> <status> [--json]

fpp escalation list [--json]                Active escalations, grouped by stage
fpp escalation status <invoice-id> [--json] Current stage + full history
fpp escalation advance <invoice-id> [--json] AI-draft the next stage's email

fpp client list [--risk-level] [--search] [--page] [--page-size] [--json]
fpp client show <client-id> [--json]
fpp client risk <client-id> [--json]        Compute/refresh the AI risk score
```

Run `fpp --help` or `fpp <command> --help` for full flag references.

![Filtering invoices, scoring a client, and checking escalation status](https://raw.githubusercontent.com/RudrenduPaul/freelancer-payment-protection/main/docs/usage.gif)

### A note on `escalation advance`

The backend's escalation router (`apps/api/app/routers/escalations.py`)
exposes exactly three routes: list active escalations, draft the next
stage's email, and read history. There is no route that persists a stage
change — `draft_escalation_email` in `escalation_service.py` computes and
returns what the next stage's email would say, but never writes
`escalation_stage` back to the database. `fpp escalation advance` calls
that draft endpoint and shows you the preview; it does not claim to move
the invoice to the next stage, because the API it wraps doesn't do that
either.

### JSON output for agents/scripts

```bash
fpp invoice list --status overdue --json | jq '.[] | {id, invoiceNumber, daysPastDue}'
fpp client risk "$CLIENT_ID" --json | jq '.level'
```

Field names in `--json` output match the backend's actual Pydantic response
models exactly (camelCase, e.g. `invoiceNumber`, `daysPastDue`,
`escalationStage`) since the CLI passes the API's response straight
through rather than remapping it.

## FAQ

**What is this, and how is it different from just calling the API with curl?**
It's a typed command-line wrapper around the same backend the web
dashboard uses — invoices, escalations, and client risk scoring — with
persistent login (so you're not re-attaching a bearer token to every
request), human-readable tables by default, and a `--json` flag on every
data command for piping into `jq`, scripts, or an agent's tool-calling
loop. The differentiator versus curl is session handling (login once,
silent token refresh after) and consistent, documented output shapes
instead of hand-rolled request construction.

**What platforms and Python versions does it support?**
Python 3.10 through 3.13, on any OS `pip`/`uvx`/`pipx` runs on (Linux,
macOS, Windows). It has no compiled dependencies — the only runtime
dependencies are `click` and `httpx`, both pure-Python-installable wheels.

**How do I log in, and where are my credentials stored?**
Run `fpp login`, enter your email and password when prompted. The CLI
calls Supabase's password-grant token endpoint directly (see "Login and
authentication" above) and caches the resulting access and refresh tokens
to `~/.config/freelancer-payment-protection-cli/credentials.json` with
file mode 600 (owner read/write only). Nothing is sent anywhere except
Supabase's own auth endpoint and the backend API you configure via
`FPP_API_URL`.

**I ran a command and got `Error: Internal Server Error` — is that a CLI bug?**
Usually not. The CLI's error handling surfaces whatever the backend
returned; a 500 means the backend itself failed. Two real, backend-side
causes to check first: (1) `fpp client risk` and `fpp escalation advance`
both trigger AI calls through `packages/legal_ai/client.py` — if
`ANTHROPIC_API_KEY` isn't a real key on the server, `client risk` falls
back to a heuristic score automatically, but `escalation advance` has no
such fallback and will 500. (2) Confirm you're running a backend build
that includes the `packages/legal_ai` module-name fix and the
`risk_scoring.py` request-parameter fix — both were real bugs in this
repo (a hyphenated `packages/legal-ai` directory that the code imports as
`packages.legal_ai`, and a rate-limiter/parameter-name collision on
`/api/v1/risk/score`) that this CLI's own end-to-end testing surfaced and
this same change fixed. A plain 401 means your cached token expired and
couldn't refresh — run `fpp login` again.

**Does `fpp escalation advance` actually send the escalation email or move the invoice to the next stage?**
No. It calls the backend's `/api/v1/escalations/{id}/draft` endpoint,
which only returns an AI-drafted preview of what the next stage's email
would say. The backend has no endpoint today that persists a stage change
or sends the email — see "A note on `escalation advance`" above.

**Can I point this at a self-hosted or non-default backend?**
Yes. Set `FPP_API_URL` to your backend's base URL (default is
`http://localhost:8000`, matching the FastAPI dev server's default port).
Every command reads that variable at call time, so switching environments
is just re-exporting it.

**What's the licensing situation — can I use or modify this commercially?**
This CLI ships from the same repository as, and under the same license
as, freelancer-payment-protection itself: a proprietary license, copyright
Rudrendu Paul and Sourav Nandy, all rights reserved. Personal, academic,
commercial, or scheduled use requires explicit written permission from
both owners — see the `LICENSE` file. This is not an MIT/Apache-style
open-source license; publishing it to PyPI makes it installable, not
freely reusable.

**Why isn't there a hosted/default API URL I can just start using?**
freelancer-payment-protection is self-hosted software, not a hosted
multi-tenant SaaS with a public API endpoint today. You (or whoever
operates your workspace) runs the backend; the CLI just needs its URL.

## Development

```bash
cd packages/cli
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

All HTTP calls (to Supabase and to the backend API) are mocked in tests
with `respx` — the test suite makes no live network calls.

## Contributing

This package lives inside the freelancer-payment-protection monorepo. See
the repository root for contribution guidelines.

## License

Proprietary — see [`LICENSE`](./LICENSE). Contact the owners (see
`LICENSE`) before any use beyond installing and running the package as
published.
