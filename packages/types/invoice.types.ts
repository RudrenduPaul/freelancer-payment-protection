export type InvoiceStatus =
  | 'paid'
  | 'pending'
  | 'overdue'
  | 'disputed'
  | 'written_off';

export type EscalationStage =
  | 'polite_reminder'
  | 'firm_notice'
  | 'final_warning'
  | 'legal_demand'
  | 'legal_action';

export interface LineItem {
  id: string;
  description: string;
  quantity: number;
  unitPrice: number;
  total: number;
}

export interface Invoice {
  id: string;
  clientId: string;
  workspaceId: string;
  invoiceNumber: string;
  amount: number;
  currency: string;
  dueDate: Date;
  status: InvoiceStatus;
  daysPastDue: number;
  escalationStage: EscalationStage | null;
  sourceSystem?: 'freshbooks' | 'quickbooks' | 'wave' | 'manual';
  externalId?: string;
  lineItems: LineItem[];
  lastEscalatedAt?: Date;
  nextEscalationDate?: Date;
  evidenceCount: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface InvoiceCreate {
  clientId: string;
  invoiceNumber: string;
  amount: number;
  currency?: string;
  dueDate: Date;
  sourceSystem?: 'freshbooks' | 'quickbooks' | 'wave' | 'manual';
  externalId?: string;
  lineItems?: LineItem[];
}
