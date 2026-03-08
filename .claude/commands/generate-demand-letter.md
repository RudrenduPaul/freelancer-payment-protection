# /generate-demand-letter <invoice_id>

Generates a jurisdiction-aware legal demand letter for the specified invoice.

## Steps
1. Fetch invoice + client data from DB (or seed data if no live DB)
2. Fetch evidence summary for this invoice
3. Call packages/legal-ai/prompts/demand_letter.py with all context
4. Generate document via apps/api/app/services/doc_gen_service.py
5. Store in Supabase Storage (or local /generated-docs/ in dev)
6. Return download path

## Checklist
- [ ] Legal disclaimer at top of document
- [ ] Jurisdiction-appropriate language
- [ ] All [PLACEHOLDER] values filled in
- [ ] Invoice number and amount correct
- [ ] Previous contact dates listed
- [ ] 7-business-day deadline set from current date
- [ ] Document is readable and well-formatted
