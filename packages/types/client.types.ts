export type ClientRiskLevel = 'low' | 'medium' | 'high' | 'critical';

export interface Client {
  id: string;
  workspaceId: string;
  name: string;
  email: string;
  company: string;
  industry: string;
  country: string;
  riskScore: number;
  riskLevel: ClientRiskLevel;
  totalInvoiced: number;
  totalOutstanding: number;
  paymentTermsDays: number;
  averagePaymentDelay: number;
  contractUrl?: string;
  notes: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface ClientCreate {
  name: string;
  email: string;
  company?: string;
  industry?: string;
  country?: string;
  paymentTermsDays?: number;
  contractUrl?: string;
  notes?: string;
}
