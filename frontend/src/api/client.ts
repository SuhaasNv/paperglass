/**
 * The API client: one fetch wrapper that speaks the backend's error shape, and one function
 * per endpoint. Same-origin `/api/v1` (Vite proxies it in development; nginx in production),
 * cookies included so the anonymous session travels with every call.
 */

import type {
  ErrorBody,
  Health,
  ScanDetail,
  ScanList,
  TechniqueList,
  Tier,
} from './types'

export const API_BASE = '/api/v1'

export class ApiError extends Error {
  readonly status: number
  readonly code: string
  readonly details: unknown

  constructor(status: number, code: string, message: string, details?: unknown) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
    this.details = details
  }
}

function isErrorBody(value: unknown): value is ErrorBody {
  if (typeof value !== 'object' || value === null || !('error' in value)) return false
  const error = (value as { error: unknown }).error
  return (
    typeof error === 'object' &&
    error !== null &&
    typeof (error as { code?: unknown }).code === 'string' &&
    typeof (error as { message?: unknown }).message === 'string'
  )
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  let response: Response
  try {
    response = await fetch(path, { credentials: 'include', ...init })
  } catch (cause) {
    throw new ApiError(0, 'network', 'The server could not be reached.', cause)
  }
  if (response.ok) {
    return (await response.json()) as T
  }
  let body: unknown = null
  try {
    body = await response.json()
  } catch {
    body = null
  }
  if (isErrorBody(body)) {
    throw new ApiError(response.status, body.error.code, body.error.message, body.error.details)
  }
  throw new ApiError(response.status, 'http_error', `The server answered ${response.status}.`)
}

export interface CreateScanInput {
  file: File
  tier: Tier
  profile: string
}

export function createScan({ file, tier, profile }: CreateScanInput): Promise<ScanDetail> {
  const form = new FormData()
  form.append('file', file, file.name)
  form.append('tier', tier)
  form.append('profile', profile)
  return request<ScanDetail>(`${API_BASE}/scans`, { method: 'POST', body: form })
}

export function getScan(id: string): Promise<ScanDetail> {
  return request<ScanDetail>(`${API_BASE}/scans/${encodeURIComponent(id)}`)
}

export function listScans(): Promise<ScanList> {
  return request<ScanList>(`${API_BASE}/scans`)
}

export function fingerprintScan(id: string, file: File): Promise<ScanDetail> {
  const form = new FormData()
  form.append('file', file, file.name)
  return request<ScanDetail>(`${API_BASE}/scans/${encodeURIComponent(id)}/fingerprint`, {
    method: 'POST',
    body: form,
  })
}

export function listTechniques(): Promise<TechniqueList> {
  return request<TechniqueList>(`${API_BASE}/techniques`)
}

export function health(): Promise<Health> {
  return request<Health>('/healthz')
}
