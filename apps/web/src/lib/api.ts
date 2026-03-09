import type {
  Client,
  ClientCreate,
  Invoice,
  InvoiceCreate,
  InvoiceStatus,
  EscalationEvent,
  ActiveEscalation,
  EvidenceItem,
  DashboardOverview,
  DemandLetterRequest,
  DemandLetterResponse,
  RiskScore,
  PaginatedResponse,
  ApiError,
} from './types'

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

class ApiClientError extends Error {
  constructor(
    public readonly status: number,
    public readonly detail: string,
  ) {
    super(detail)
    this.name = 'ApiClientError'
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (res.ok) {
    // 204 No Content
    if (res.status === 204) return undefined as unknown as T
    return res.json() as Promise<T>
  }

  let detail = `HTTP ${res.status}: ${res.statusText}`
  try {
    const body = (await res.json()) as ApiError
    if (body.detail) detail = body.detail
  } catch {
    // keep default message
  }

  throw new ApiClientError(res.status, detail)
}

async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
    cache: 'no-store',
  })
  return handleResponse<T>(res)
}

async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  return handleResponse<T>(res)
}

async function apiPatch<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  return handleResponse<T>(res)
}

async function apiDelete(path: string): Promise<void> {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
  })
  return handleResponse<void>(res)
}

// ─── Clients ─────────────────────────────────────────────────────────────────

export const clientsApi = {
  list(): Promise<PaginatedResponse<Client>> {
    return apiGet('/api/v1/clients')
  },

  create(data: ClientCreate): Promise<Client> {
    return apiPost('/api/v1/clients', data)
  },

  get(id: string): Promise<Client> {
    return apiGet(`/api/v1/clients/${id}`)
  },

  update(id: string, data: Partial<ClientCreate>): Promise<Client> {
    return apiPatch(`/api/v1/clients/${id}`, data)
  },

  delete(id: string): Promise<void> {
    return apiDelete(`/api/v1/clients/${id}`)
  },

  getRiskScore(id: string): Promise<RiskScore> {
    return apiGet(`/api/v1/clients/${id}/risk-score`)
  },
}

// ─── Invoices ─────────────────────────────────────────────────────────────────

export interface InvoiceFilters {
  clientId?: string
  status?: InvoiceStatus
  page?: number
  pageSize?: number
}

export const invoicesApi = {
  list(filters?: InvoiceFilters): Promise<PaginatedResponse<Invoice>> {
    const params = new URLSearchParams()
    if (filters?.clientId) params.set('client_id', filters.clientId)
    if (filters?.status) params.set('status', filters.status)
    if (filters?.page !== undefined) params.set('page', String(filters.page))
    if (filters?.pageSize !== undefined)
      params.set('page_size', String(filters.pageSize))
    const qs = params.toString()
    return apiGet(`/api/v1/invoices${qs ? `?${qs}` : ''}`)
  },

  create(data: InvoiceCreate): Promise<Invoice> {
    return apiPost('/api/v1/invoices', data)
  },

  get(id: string): Promise<Invoice> {
    return apiGet(`/api/v1/invoices/${id}`)
  },

  updateStatus(id: string, status: InvoiceStatus): Promise<Invoice> {
    return apiPatch(`/api/v1/invoices/${id}/status`, { status })
  },

  getEvidence(id: string): Promise<EvidenceItem[]> {
    return apiGet(`/api/v1/invoices/${id}/evidence`)
  },

  async uploadEvidence(
    id: string,
    file: File,
    description?: string,
  ): Promise<EvidenceItem> {
    const formData = new FormData()
    formData.append('file', file)
    if (description) formData.append('description', description)

    const res = await fetch(`${BASE_URL}/api/v1/invoices/${id}/evidence`, {
      method: 'POST',
      body: formData,
    })
    return handleResponse<EvidenceItem>(res)
  },
}

// ─── Escalations ──────────────────────────────────────────────────────────────

export const escalationsApi = {
  listActive(): Promise<ActiveEscalation[]> {
    return apiGet('/api/v1/escalations/active')
  },

  getHistory(invoiceId: string): Promise<EscalationEvent[]> {
    return apiGet(`/api/v1/escalations/history/${invoiceId}`)
  },

  draftEmail(invoiceId: string): Promise<EscalationEvent> {
    return apiPost(`/api/v1/escalations/${invoiceId}/draft`, {})
  },

  sendEmail(invoiceId: string): Promise<EscalationEvent> {
    return apiPost(`/api/v1/escalations/${invoiceId}/send`, {})
  },
}

// ─── Analytics ────────────────────────────────────────────────────────────────

export const analyticsApi = {
  getOverview(): Promise<DashboardOverview> {
    return apiGet('/api/v1/analytics/overview')
  },
}

// ─── Legal Docs ───────────────────────────────────────────────────────────────

export const legalDocsApi = {
  create(data: DemandLetterRequest): Promise<DemandLetterResponse> {
    return apiPost('/api/v1/legal/demand-letter', data)
  },

  streamUrl(invoiceId: string, jurisdiction: string): string {
    const params = new URLSearchParams({ jurisdiction })
    return `${BASE_URL}/api/v1/legal/demand-letter/${invoiceId}/stream?${params}`
  },
}

export { ApiClientError }
