export interface ApiError {
  detail: string;
  code?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface DemandLetterRequest {
  invoiceId: string;
  jurisdiction: string;
  clientName: string;
  clientCompany?: string;
  amount: number;
  currency: string;
  daysPastDue: number;
  evidenceSummary?: string;
  previousContactDates?: string[];
}

export interface DemandLetterResponse {
  documentId: string;
  status: 'generating' | 'ready' | 'failed';
  estimatedReadySeconds?: number;
  downloadUrl?: string;
}
