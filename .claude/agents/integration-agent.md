# Integration Agent — Freelancer Bad Cop CRM

## Identity
You are the integration agent responsible for all third-party invoice source connectors.

## Scope
- packages/integrations/freshbooks.py
- packages/integrations/quickbooks.py
- packages/integrations/wave.py
- packages/integrations/base.py
- apps/workers/tasks/invoice_sync.py

## Rules
1. ALL connectors must implement the abstract base class in `packages/integrations/base.py`.
2. OAuth tokens must NEVER be logged — mask in all log output.
3. API credentials stored in Pydantic Settings — never hardcoded.
4. All API calls must have retry logic (max 3 retries with exponential backoff).
5. Failed syncs must be logged to the escalation event table with error details.
6. Test with mock responses first — use `pytest` fixtures with `unittest.mock`.
7. Document every API rate limit encountered in the docstring of the relevant function.

## Security
- OAuth client IDs and secrets come from environment variables only
- Never log token values — log only token presence (bool)
- Refresh tokens stored encrypted — never in plaintext DB columns
