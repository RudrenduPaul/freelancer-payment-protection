# /review-pr

Perform a security + performance + MLP lovability review on the current changes.

## Security Review Checklist
- [ ] No secrets, API keys, or credentials in code or tests
- [ ] No hardcoded passwords or tokens anywhere
- [ ] All new API endpoints have Pydantic validation
- [ ] All new DB tables have RLS policies
- [ ] Input that reaches the DB goes through SQLAlchemy ORM (no raw SQL)
- [ ] No sensitive data logged

## Performance Checklist
- [ ] No N+1 queries (check for missing eager loading)
- [ ] Indexes added for new query patterns
- [ ] Background jobs used for expensive operations (AI calls, PDF gen, email)

## MLP Lovability Checklist
- [ ] Empty states have personality copy (not "No data found")
- [ ] Appropriate Framer Motion animation present
- [ ] Error states are friendly, not raw error codes
- [ ] AI outputs display confidence score in UI
- [ ] Legal documents display the required disclaimer

## Test Checklist
- [ ] New feature has happy path test
- [ ] New feature has auth failure test
- [ ] New feature has validation error test
- [ ] Coverage does not drop below 70%
- [ ] No live API calls in test suite (all mocked)
