## What This PR Does
[1-2 sentences]

## Type
- [ ] Feature
- [ ] Bug fix
- [ ] Security fix
- [ ] Refactoring
- [ ] Docs

## MLP Lovability Checklist
- [ ] Empty states have personality copy (not "No data found")
- [ ] Appropriate Framer Motion animation present
- [ ] Error states are friendly, not technical error codes
- [ ] AI outputs display confidence score in UI
- [ ] Legal documents display the required disclaimer

## Security Checklist
- [ ] No secrets in code (API keys, tokens, passwords)
- [ ] No hardcoded credentials anywhere in added/modified files
- [ ] All new API endpoints have Pydantic validation
- [ ] All new DB tables have RLS policies
- [ ] Input that reaches the DB goes through SQLAlchemy ORM
- [ ] No raw SQL strings

## Tests
- [ ] New feature has happy path test
- [ ] New feature has auth failure test
- [ ] New feature has validation error test
- [ ] Coverage does not drop below 70%
- [ ] No live API calls in test suite (all mocked)

## Legal AI Checklist (if applicable)
- [ ] Generated documents include the AI/non-legal-advice disclaimer
- [ ] No fabricated case law or statutes
- [ ] Jurisdiction is explicitly set in the prompt
- [ ] [PLACEHOLDER] used for any missing information
