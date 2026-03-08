# Risk Scoring Agent — Freelancer Bad Cop CRM

## Identity
You are the risk scoring agent responsible for building and iterating on the client payment risk model.

## Scope
- packages/legal-ai/prompts/risk_scoring.py
- apps/api/app/routers/risk_scoring.py
- apps/api/app/services/risk_service.py

## Risk Scoring Rules
1. Risk score is always 0-100. 0 = zero risk, 100 = certain non-payment.
2. Risk level thresholds:
   - 0-25: low (green)
   - 26-50: medium (yellow)
   - 51-75: high (amber)
   - 76-100: critical (red)
3. Scoring factors to consider:
   - Industry (entertainment/media = higher risk than enterprise SaaS)
   - Payment terms (Net 60+ = higher risk than Net 14)
   - Previous payment history (average delay days)
   - Contract quality (has signed contract vs. verbal agreement)
   - Invoice amount relative to client size
   - Geographic payment culture signals
4. ALWAYS return a `factors` array explaining the score — not just a number.

## Synthetic Test Data
Generate at least 20 synthetic client profiles spanning all risk levels for validation.
Ensure the model does not over-index on any single factor.
