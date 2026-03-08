import type { EscalationStage } from './invoice.types';
import type { ClientRiskLevel } from './client.types';

export interface EscalationEvent {
  id: string;
  invoiceId: string;
  clientId: string;
  stage: EscalationStage;
  emailSubject: string;
  emailBody: string;
  generatedByAI: boolean;
  aiConfidenceScore?: number;
  sentAt?: Date;
  openedAt?: Date;
  repliedAt?: Date;
  outcome?: 'paid' | 'partial' | 'disputed' | 'no_response';
  documentUrl?: string;
}

export interface EvidenceItem {
  id: string;
  invoiceId: string;
  workspaceId: string;
  type: 'email' | 'slack_message' | 'contract' | 'screenshot' | 'document';
  source: 'gmail' | 'slack' | 'manual_upload' | 'auto_captured';
  filename: string;
  storageUrl: string;
  capturedAt: Date;
  metadata: Record<string, unknown>;
}

export interface DashboardMetrics {
  totalOutstanding: number;
  totalClients: number;
  overdueInvoices: number;
  escalationsActive: number;
  recoveryRateThisMonth: number;
  averageDaysToPayment: number;
  clientsByRiskLevel: Record<ClientRiskLevel, number>;
}

export interface RiskScoreResult {
  score: number;
  level: ClientRiskLevel;
  factors: Array<{
    name: string;
    impact: 'positive' | 'negative' | 'neutral';
    description: string;
    weight: number;
  }>;
  reasoning: string;
}
