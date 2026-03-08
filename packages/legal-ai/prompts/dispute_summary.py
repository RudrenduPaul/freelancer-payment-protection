"""
Prompt template for dispute summary generation.
Produces court-ready narrative from evidence timeline.
"""

DISPUTE_SUMMARY_SYSTEM = """You are a legal documentation assistant. You create clear, factual dispute summaries for freelancers preparing for small claims court or formal dispute resolution.

Your summaries are:
- Factual and chronological — no editorializing
- Specific — exact dates, amounts, invoice numbers
- Professional — appropriate for submission to a court or arbitrator
- Complete — cover the full engagement history

Always include the AI disclaimer. Never fabricate dates or facts not provided."""


def build_dispute_summary_prompt(
    client_name: str,
    freelancer_name: str,
    invoice_number: str,
    amount: float,
    currency: str,
    engagement_description: str,
    evidence_timeline: list[dict],
) -> str:
    timeline_str = "\n".join([
        f"- {item.get('date', 'Unknown date')}: {item.get('description', '')}"
        for item in evidence_timeline
    ])

    return f"""Create a formal dispute summary document for the following case:

FREELANCER: {freelancer_name}
CLIENT: {client_name}
INVOICE: {invoice_number}
AMOUNT IN DISPUTE: {currency} {amount:,.2f}
ENGAGEMENT: {engagement_description}

EVIDENCE TIMELINE:
{timeline_str if timeline_str else "No formal timeline provided."}

Create a structured dispute summary including:
1. AI disclaimer at the top
2. Executive summary of the dispute
3. Chronological timeline of events
4. Description of services delivered and agreed payment terms
5. Communication history (attempts to collect)
6. Current status and requested resolution
7. List of attached evidence

Format as a formal document suitable for small claims court submission."""
