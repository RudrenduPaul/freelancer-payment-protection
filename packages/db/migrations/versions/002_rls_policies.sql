-- RLS policies for Supabase PostgreSQL
-- Apply these in the Supabase SQL editor after running Alembic migrations.
-- These policies enforce workspace-level data isolation at the DB layer.

ALTER TABLE clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE escalation_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE evidence_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE workspaces ENABLE ROW LEVEL SECURITY;

-- Workspace isolation: users only see data in their workspace
CREATE POLICY "workspace_isolation_clients"
ON clients FOR ALL
USING (workspace_id = (auth.jwt() ->> 'workspace_id')::uuid);

CREATE POLICY "workspace_isolation_invoices"
ON invoices FOR ALL
USING (workspace_id = (auth.jwt() ->> 'workspace_id')::uuid);

CREATE POLICY "workspace_isolation_escalations"
ON escalation_events FOR ALL
USING (
  invoice_id IN (
    SELECT id FROM invoices
    WHERE workspace_id = (auth.jwt() ->> 'workspace_id')::uuid
  )
);

CREATE POLICY "workspace_isolation_evidence"
ON evidence_items FOR ALL
USING (workspace_id = (auth.jwt() ->> 'workspace_id')::uuid);

-- Only workspace owners can delete clients
CREATE POLICY "owner_delete_only_clients"
ON clients FOR DELETE
USING (
  workspace_id IN (
    SELECT id FROM workspaces WHERE owner_id = auth.uid()
  )
);

CREATE POLICY "member_read_evidence"
ON evidence_items FOR SELECT
USING (workspace_id = (auth.jwt() ->> 'workspace_id')::uuid);

CREATE POLICY "owner_delete_evidence"
ON evidence_items FOR DELETE
USING (
  workspace_id IN (
    SELECT id FROM workspaces WHERE owner_id = auth.uid()
  )
);
