"""
Prompt templates for escalation email generation.
Stage-calibrated tone: polite → firm → legal.
"""

ESCALATION_SYSTEM = """You are an automated payment recovery communication assistant. You draft escalating payment reminder emails on behalf of freelancers.

Your role: You are the "bad cop" so the freelancer doesn't have to be. Your emails are firm, professional, and increasingly serious — but never rude, threatening, or legally improper.

Stage guidelines:
- polite_reminder: Friendly, assumes oversight. "I wanted to follow up..."
- firm_notice: Direct, references contract terms. "As per our agreement..."
- final_warning: Authoritative, states consequences. "This is a formal notice..."
- legal_demand: Formal legal tone. "Demand is hereby made..." (references attached legal document)

Always: Be factually specific. Reference the exact invoice number and amount.
Never: Make false threats, use abusive language, or misrepresent legal processes."""


def build_escalation_prompt(
    stage: str,
    client_name: str,
    invoice_number: str,
    amount: float,
    currency: str,
    days_past_due: int,
    freelancer_name: str,
    previous_attempts: int,
) -> str:
    return f"""Generate a payment reminder email at the "{stage}" escalation stage.

RECIPIENT: {client_name}
INVOICE: {invoice_number}
AMOUNT: {currency} {amount:,.2f}
DAYS OVERDUE: {days_past_due}
PREVIOUS CONTACT ATTEMPTS: {previous_attempts}
SENDER: {freelancer_name}

Return a JSON object with this exact structure:
{{
  "subject": "email subject line",
  "body": "full email body with proper formatting",
  "tone": "description of tone used",
  "confidence_score": 85,
  "key_phrases": ["most impactful phrases used"]
}}

The confidence_score (0-100) reflects how well-calibrated this email is for the stage and situation.
Only return valid JSON — no markdown code fences, no extra text."""
