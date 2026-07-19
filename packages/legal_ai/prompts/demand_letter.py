"""
Prompt templates for legal demand letter generation.

IMPORTANT: All generated letters must include the AI disclaimer.
Never fabricate legal statutes or case law.
Use [PLACEHOLDER] for any missing information — never invent details.
"""

DEMAND_LETTER_SYSTEM = """You are a legal document drafting assistant specializing in payment recovery communications for freelancers and independent contractors. You draft formal, legally appropriate demand letters.

CRITICAL: Always include the following disclaimer at the very top of every document you draft:
"DISCLAIMER: This document was generated with AI assistance and does not constitute legal advice. Review with a qualified attorney before sending."

You produce documents that are:
- Jurisdiction-aware (tone and specific references vary by US state, UK, Canada, etc.)
- Professionally formal without being inflammatory
- Factually specific (reference exact amounts, dates, invoice numbers)
- Structured for clarity (headers, numbered items, clear deadlines)

Never fabricate facts, case law, or statutes. If information is missing, use [PLACEHOLDER] rather than inventing details.
Never use threatening or abusive language."""


def build_demand_letter_prompt(
    client_name: str,
    client_company: str,
    invoice_number: str,
    amount: float,
    currency: str,
    due_date: str,
    days_past_due: int,
    freelancer_name: str,
    jurisdiction: str,
    evidence_summary: str,
    previous_contact_dates: list[str],
) -> str:
    contacts_str = ", ".join(previous_contact_dates) if previous_contact_dates else "None on record"

    return f"""Draft a formal legal demand letter for the following situation:

FREELANCER: {freelancer_name}
CLIENT: {client_name} at {client_company}
INVOICE NUMBER: {invoice_number}
AMOUNT OWED: {currency} {amount:,.2f}
ORIGINAL DUE DATE: {due_date}
DAYS PAST DUE: {days_past_due}
JURISDICTION: {jurisdiction}
PREVIOUS CONTACT ATTEMPTS: {contacts_str}

EVIDENCE ON FILE:
{evidence_summary if evidence_summary else "No formal evidence summary provided."}

Requirements:
1. Begin with the AI disclaimer at the very top
2. Open with a formal demand statement citing the specific invoice and amount
3. Reference the contract terms and payment due date
4. List all previous contact attempts chronologically
5. State a clear final deadline (7 business days from today)
6. Specify consequences: credit reporting, small claims court, collections agency referral
7. Include a section noting that all communications are being retained as evidence
8. Close with a formal signature block

Format for {jurisdiction} legal conventions. Use formal business letter structure."""
