# /new-escalation-template <stage>

Scaffolds a new escalation email template for the given stage.

## Steps
1. Create prompt template in packages/legal-ai/prompts/escalation_sequence.py
2. Add stage to EscalationStage enum if not present
3. Create React Email template in apps/web/emails/<stage>.tsx
4. Add preview route in apps/web/app/api/email-preview/<stage>/route.ts
5. Write pytest test: apps/api/tests/test_escalations.py::test_<stage>_generation

## Template Requirements
- Reference invoice number and amount
- Include previous contact count
- Tone calibrated to stage (see escalation-agent.md rules)
- Subject line A/B variants (provide 2)
- Confidence score returned from Claude
