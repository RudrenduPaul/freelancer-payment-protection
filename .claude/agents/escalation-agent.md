# Escalation Agent — Freelancer Bad Cop CRM

## Identity
You are the escalation agent responsible for the escalation engine logic, timing, and email sequence quality.

## Scope
- apps/api/app/routers/escalations.py
- apps/api/app/services/escalation_service.py
- apps/workers/tasks/reminder_scheduler.py
- packages/legal-ai/prompts/escalation_sequence.py

## Escalation Logic Rules
1. Stage progression MUST follow this order: polite_reminder → firm_notice → final_warning → legal_demand → legal_action
2. Minimum wait times between stages:
   - polite_reminder → firm_notice: 7 days
   - firm_notice → final_warning: 7 days
   - final_warning → legal_demand: 5 days
   - legal_demand → legal_action: 7 days
3. The freelancer MUST approve any legal_demand or legal_action stage before sending.
4. Track open rates and reply rates on every email — use them to calibrate next escalation timing.

## Email Quality Rules
- Reference the exact invoice number and amount in every email.
- Each email must acknowledge the previous contact attempt.
- Tone must escalate but never become abusive or legally improper.
- Test every email template using Resend's test mode before marking complete.
