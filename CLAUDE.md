# Freelancer "Bad Cop" CRM — Claude Code Instructions

## What This Product Does
An AI-native payment protection SaaS for freelancers. Automates invoice escalation,
legal document generation, and client risk scoring. The product is the "bad cop" so
the freelancer stays the "good cop."

## Stack
- Frontend: Next.js 14 App Router + Tailwind CSS + shadcn/ui + Framer Motion
- Backend: Python 3.12 + FastAPI
- Database: Supabase (PostgreSQL + Auth + Storage + RLS)
- Dev DB: SQLite via SQLAlchemy (seed data, no credentials needed)
- AI: Anthropic Claude API (claude-sonnet-4-6) via packages/legal-ai/client.py
- Queue: Celery + Redis
- Email: Resend + React Email
- Document Gen: python-docx + WeasyPrint
- Monorepo: Turborepo + pnpm workspaces
- Testing: pytest + Playwright

## Security Rules — Non-Negotiable
1. NEVER hardcode API keys, secrets, or credentials anywhere in the codebase
2. ALL secrets go in .env files only — .env files are gitignored
3. NEVER commit .env files — only .env.example with placeholder values
4. All AI calls MUST use packages/legal-ai/client.py — never call Anthropic SDK directly
5. ALL AI-generated legal documents MUST include the legal disclaimer
6. RLS policies protect ALL tables — workspace_id isolation is non-negotiable
7. All secrets via Pydantic Settings — never in client bundle

## Hard Coding Rules
1. NEVER use `any` TypeScript types — use proper types from packages/types/
2. DB changes go in packages/db/migrations/versions/ via Alembic — never edit schema directly
3. Run `pnpm lint && pnpm typecheck` (frontend) and `pytest` (backend) before every commit
4. Mock ALL external API calls in tests — no live API calls in test suite

## Escalation Stage Order
polite_reminder → firm_notice → final_warning → legal_demand → legal_action

## Minimum Wait Times Between Stages
- polite_reminder → firm_notice: 7 days
- firm_notice → final_warning: 7 days
- final_warning → legal_demand: 5 days
- legal_demand → legal_action: 7 days

## Risk Score Thresholds
0-25: low (green) | 26-50: medium (yellow) | 51-75: high (amber) | 76-100: critical (red)

## MLP Gate — Before Marking Any Feature Done
- [ ] Empty state has personality copy (not "No data found")
- [ ] Appropriate Framer Motion animation present
- [ ] Error states are friendly, not technical error codes
- [ ] AI outputs show confidence score in UI
- [ ] Legal docs show disclaimer prominently

## Custom Commands
/new-escalation-template <stage>      → scaffold new escalation email template + test
/generate-demand-letter <invoice_id>  → generate demand letter for specific invoice
/review-pr                            → security + performance + MLP lovability review

## Sub-Agents Available
.claude/agents/legal-ai-agent.md
.claude/agents/escalation-agent.md
.claude/agents/integration-agent.md
.claude/agents/risk-scoring-agent.md
.claude/agents/evidence-locker-agent.md
.claude/agents/test-agent.md
