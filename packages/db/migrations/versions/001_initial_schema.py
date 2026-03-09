"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-03-01
"""
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'workspaces',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('owner_id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False, unique=True),
        sa.Column('plan', sa.String(20), default='solo'),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
    )
    op.create_index('ix_workspaces_owner', 'workspaces', ['owner_id'])

    op.create_table(
        'clients',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('workspace_id', sa.String(36), sa.ForeignKey('workspaces.id'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('company', sa.String(255)),
        sa.Column('industry', sa.String(100)),
        sa.Column('country', sa.String(2)),
        sa.Column('risk_score', sa.Float, default=0.0),
        sa.Column('risk_level', sa.String(20), default='low'),
        sa.Column('total_invoiced', sa.Float, default=0.0),
        sa.Column('total_outstanding', sa.Float, default=0.0),
        sa.Column('payment_terms_days', sa.Integer, default=30),
        sa.Column('average_payment_delay', sa.Float, default=0.0),
        sa.Column('contract_url', sa.String(500)),
        sa.Column('notes', sa.String(5000)),
        sa.Column('deleted_at', sa.DateTime),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
    )
    op.create_index('ix_clients_workspace_id', 'clients', ['workspace_id'])
    op.create_index('ix_clients_workspace_risk', 'clients', ['workspace_id', 'risk_level'])

    op.create_table(
        'invoices',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('client_id', sa.String(36), sa.ForeignKey('clients.id'), nullable=False),
        sa.Column('workspace_id', sa.String(36), sa.ForeignKey('workspaces.id'), nullable=False),
        sa.Column('invoice_number', sa.String(100), nullable=False),
        sa.Column('amount', sa.Float, nullable=False),
        sa.Column('currency', sa.String(3), default='USD'),
        sa.Column('due_date', sa.DateTime, nullable=False),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('days_past_due', sa.Integer, default=0),
        sa.Column('escalation_stage', sa.String(50)),
        sa.Column('source_system', sa.String(50)),
        sa.Column('external_id', sa.String(255)),
        sa.Column('line_items', sa.JSON, default=list),
        sa.Column('last_escalated_at', sa.DateTime),
        sa.Column('next_escalation_date', sa.DateTime),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
    )
    op.create_index('ix_invoices_workspace_id', 'invoices', ['workspace_id'])
    op.create_index('ix_invoices_workspace_status', 'invoices', ['workspace_id', 'status'])
    op.create_index('ix_invoices_client_status', 'invoices', ['client_id', 'status'])

    op.create_table(
        'escalation_events',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('invoice_id', sa.String(36), sa.ForeignKey('invoices.id'), nullable=False),
        sa.Column('workspace_id', sa.String(36), sa.ForeignKey('workspaces.id'), nullable=False),
        sa.Column('client_id', sa.String(36), nullable=False),
        sa.Column('stage', sa.String(50), nullable=False),
        sa.Column('email_subject', sa.String(500)),
        sa.Column('email_body', sa.String(10000)),
        sa.Column('generated_by_ai', sa.Boolean, default=True),
        sa.Column('ai_confidence_score', sa.Float),
        sa.Column('sent_at', sa.DateTime),
        sa.Column('opened_at', sa.DateTime),
        sa.Column('replied_at', sa.DateTime),
        sa.Column('outcome', sa.String(50)),
        sa.Column('document_url', sa.String(500)),
        sa.Column('created_at', sa.DateTime, nullable=False),
    )
    op.create_index('ix_escalation_workspace', 'escalation_events', ['workspace_id'])
    op.create_index('ix_escalation_invoice', 'escalation_events', ['invoice_id'])

    op.create_table(
        'evidence_items',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('invoice_id', sa.String(36), sa.ForeignKey('invoices.id'), nullable=False),
        sa.Column('workspace_id', sa.String(36), sa.ForeignKey('workspaces.id'), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('source', sa.String(50), nullable=False),
        sa.Column('filename', sa.String(500), nullable=False),
        sa.Column('storage_url', sa.String(1000), nullable=False),
        sa.Column('file_hash', sa.String(64)),
        sa.Column('file_size_bytes', sa.String(20)),
        sa.Column('captured_at', sa.DateTime, nullable=False),
        sa.Column('metadata', sa.JSON, default=dict),
    )
    op.create_index('ix_evidence_workspace', 'evidence_items', ['workspace_id'])
    op.create_index('ix_evidence_invoice', 'evidence_items', ['invoice_id'])


def downgrade() -> None:
    op.drop_index('ix_evidence_invoice')
    op.drop_index('ix_evidence_workspace')
    op.drop_table('evidence_items')
    op.drop_index('ix_escalation_invoice')
    op.drop_index('ix_escalation_workspace')
    op.drop_table('escalation_events')
    op.drop_index('ix_invoices_client_status')
    op.drop_index('ix_invoices_workspace_status')
    op.drop_index('ix_invoices_workspace_id')
    op.drop_table('invoices')
    op.drop_index('ix_clients_workspace_risk')
    op.drop_index('ix_clients_workspace_id')
    op.drop_table('clients')
    op.drop_index('ix_workspaces_owner')
    op.drop_table('workspaces')
