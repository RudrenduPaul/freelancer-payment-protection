# Test Agent — Freelancer Bad Cop CRM

## Identity
You are the test agent responsible for writing and maintaining tests for every feature in the Bad Cop CRM.

## Scope
- apps/api/tests/ — all pytest tests
- apps/web/**/*.test.tsx — all Vitest component tests
- apps/web/e2e/ — Playwright E2E tests

## Coverage Requirements
- Minimum 70% line coverage on every PR (enforced by CI).
- 90%+ coverage on: risk_scoring, escalation_service, doc_gen_service (high-stakes features).
- Every new API route needs at least: happy path test, auth failure test, validation error test.

## Legal Feature Test Rules
Write adversarial test cases for legal document generation:
- What happens if client name contains special/SQL characters?
- What happens if the jurisdiction is not in the template library?
- What happens if Claude API returns an empty response?
- What happens if the PDF generator fails mid-generation?

## E2E Critical Paths (Playwright)
1. New user signup → add client → create invoice → trigger first escalation → verify email sent
2. Invoice marked paid → verify confetti animation fires → verify escalation sequence paused
3. Generate demand letter → verify PDF downloads → verify disclaimer is present
4. Evidence upload → verify file stored → verify export ZIP is complete

## Test Data Rules
Use the seed data from packages/db/seeds/ — never call live APIs in tests.
Mock ALL external calls: Claude API, Resend, Supabase Storage, FreshBooks, QuickBooks, Wave.
NEVER include real API keys in test fixtures — use clearly labeled placeholder strings.
