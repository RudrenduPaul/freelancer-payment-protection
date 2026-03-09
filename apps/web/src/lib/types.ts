// Risk
export type RiskLevel = 'low' | 'medium' | 'high' | 'critical'

export interface RiskFactor {
  name: string
  impact: 'positive' | 'negative' | 'neutral'
  description: string
  weight: number
}

export interface RiskScore {
  score: number
  level: RiskLevel
  factors: RiskFactor[]
  reasoning: string
}

// Client
export interface Client {
  id: string
  workspaceId: string
  name: string
  email: string
  company: string | null
  industry: string | null
  country: string | null
  riskScore: number
  riskLevel: RiskLevel
  totalInvoiced: number
  totalOutstanding: number
  paymentTermsDays: number
  averagePaymentDelay: number
  contractUrl: string | null
  notes: string | null
  createdAt: string
  updatedAt: string
}

export interface ClientCreate {
  name: string
  email: string
  company?: string
  industry?: string
  country?: string
  paymentTermsDays?: number
  contractUrl?: string
  notes?: string
}

// Invoice
export type InvoiceStatus =
  | 'draft'
  | 'sent'
  | 'overdue'
  | 'disputed'
  | 'paid'
  | 'written_off'

export type EscalationStage =
  | 'polite_reminder'
  | 'firm_notice'
  | 'final_warning'
  | 'legal_demand'
  | 'legal_action'

export interface LineItem {
  description: string
  quantity: number
  unitPrice: number
  total: number
}

export interface Invoice {
  id: string
  workspaceId: string
  clientId: string
  clientName?: string
  invoiceNumber: string
  status: InvoiceStatus
  amount: number
  currency: string
  issueDate: string
  dueDate: string
  paidAt: string | null
  escalationStage: EscalationStage | null
  lineItems: LineItem[]
  notes: string | null
  evidenceCount: number
  createdAt: string
  updatedAt: string
}

export interface InvoiceCreate {
  clientId: string
  invoiceNumber: string
  amount: number
  currency?: string
  issueDate: string
  dueDate: string
  lineItems?: LineItem[]
  notes?: string
}

// Escalation
export interface EscalationEvent {
  id: string
  invoiceId: string
  workspaceId: string
  clientId: string
  stage: EscalationStage
  emailSubject: string | null
  emailBody: string | null
  generatedByAi: boolean
  aiConfidenceScore: number | null
  sentAt: string | null
  openedAt: string | null
  repliedAt: string | null
  outcome: string | null
  documentUrl: string | null
  createdAt: string
}

export interface ActiveEscalation {
  invoiceId: string
  invoiceNumber: string
  clientName: string
  clientCompany: string | null
  amount: number
  currency: string
  stage: EscalationStage
  daysPastDue: number
  nextActionDate: string | null
}

// Evidence
export interface EvidenceItem {
  id: string
  invoiceId: string
  workspaceId: string
  fileType: string
  fileName: string
  fileSizeBytes: number
  storageUrl: string
  description: string | null
  uploadedAt: string
}

// Analytics
export interface DashboardOverview {
  totalOutstanding: number
  totalClients: number
  overdueInvoices: number
  escalationsActive: number
  recoveryRateThisMonth: number
  averageDaysToPayment: number
  clientsByRiskLevel: Record<RiskLevel, number>
}

// Legal docs
export interface DemandLetterRequest {
  invoiceId: string
  jurisdiction: string
  evidenceSummary?: string
}

export interface DemandLetterResponse {
  documentUrl: string
  generatedAt: string
  jurisdiction: string
  disclaimerIncluded: boolean
}

// API generic
export interface ApiError {
  detail: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
}
