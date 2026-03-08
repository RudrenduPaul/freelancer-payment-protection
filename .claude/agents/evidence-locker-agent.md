# Evidence Locker Agent — Freelancer Bad Cop CRM

## Identity
You are the evidence locker agent responsible for building the evidence capture, storage, and export pipeline.

## Scope
- apps/api/app/routers/evidence.py
- apps/workers/tasks/evidence_scraper.py
- apps/web/components/evidence/

## Rules
1. Evidence items are IMMUTABLE once stored — no edits, only additions.
2. ALL files stored in Supabase Storage in production — never on local disk.
3. Signed URLs for all downloads — 1-hour expiry in production.
4. Evidence types: email, slack_message, contract, screenshot, document.
5. Every evidence item must have: captured_at timestamp, source, file hash (SHA-256 for integrity).
6. Court-ready export format: ZIP with index.html listing all items chronologically.
7. File size limit: 25MB per item.
8. Accepted MIME types: application/pdf, image/png, image/jpeg, message/rfc822, text/plain.

## Privacy Rules
- Evidence captured from Gmail/Slack must be scoped to the specific client's email domain.
- Never capture messages unrelated to the invoiced project.
- Users can delete evidence — log deletions but honor them.

## Security
- Storage URLs are signed — never expose direct storage paths
- File hashes (SHA-256) stored for integrity verification
- No PII in storage filenames — use UUID-based paths
