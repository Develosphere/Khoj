import { supabase } from '../lib/supabase'

export type DashboardStats = {
  total_cases: number
  active_cases: number
  total_sources: number
  total_evidence: number
  total_theories: number
}

async function responseError(response: Response) {
  const body = await response.json().catch(() => null) as { detail?: string } | null
  return body?.detail || `Request failed (${response.status})`
}

export async function apiRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  const { data, error } = await supabase.auth.getSession()
  if (error) throw error
  const token = data.session?.access_token
  if (!token) throw new Error('Your session has expired. Please sign in again.')

  const headers = new Headers(init.headers)
  headers.set('Authorization', `Bearer ${token}`)
  if (init.body && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json')

  const response = await fetch(path, { ...init, headers })
  if (!response.ok) throw new Error(await responseError(response))
  return response.json() as Promise<T>
}

export const apiService = {
  getCases: () => apiRequest<any[]>('/api/v1/cases/'),
  getDashboardStats: () => apiRequest<DashboardStats>('/api/v1/dashboard/stats'),
  createCase: (input: { title: string; description?: string }) =>
    apiRequest<any>('/api/v1/cases/', { method: 'POST', body: JSON.stringify(input) }),
  updateCase: (id: string, input: { title?: string; description?: string; status?: string }) =>
    apiRequest<any>(`/api/v1/cases/${encodeURIComponent(id)}`, { method: 'PUT', body: JSON.stringify(input) }),
  deleteCase: (id: string) =>
    apiRequest<{ status: string }>(`/api/v1/cases/${encodeURIComponent(id)}`, { method: 'DELETE' }),
  getCaseDetails: (id: string) => apiRequest<any>(`/api/v1/cases/${encodeURIComponent(id)}`),
  analyzeCase: (id: string) => apiRequest<any>(`/api/v1/cases/${encodeURIComponent(id)}/analyze`, { method: 'POST' }),
  searchSources: (query: string) => apiRequest<any>(`/api/v1/investigations/sources?case_name=${encodeURIComponent(query)}`),
  addSourceToCase: (id: string, source: unknown) =>
    apiRequest<any>(`/api/v1/cases/${encodeURIComponent(id)}/sources`, { method: 'POST', body: JSON.stringify(source) }),
}
