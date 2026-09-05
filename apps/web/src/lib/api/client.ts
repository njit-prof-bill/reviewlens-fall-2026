/**
 * Single entry point for backend calls.
 *
 * Every non-OK response becomes an ApiError carrying a message that is safe to
 * show a user; raw response bodies are never surfaced directly.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const GENERIC_MESSAGE = 'Something went wrong. Please try again.'

export interface ApiErrorDetail {
  field: string | null
  issue: string
  context?: Record<string, unknown> | null
}

export class ApiError extends Error {
  readonly status: number
  readonly code: string
  readonly details: ApiErrorDetail[]

  constructor(status: number, code: string, message: string, details: ApiErrorDetail[] = []) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
    this.details = details
  }

  get isNotFound() {
    return this.status === 404
  }

  get isUnauthorized() {
    return this.status === 401
  }

  /** Message for a specific form field, when the backend attributed one. */
  fieldIssue(field: string): string | undefined {
    return this.details.find((detail) => detail.field === field)?.issue
  }

  /** The most specific user-facing message available. */
  get displayMessage(): string {
    return this.details[0]?.issue || this.message || GENERIC_MESSAGE
  }
}

type TokenGetter = () => Promise<string | null>

export interface RequestOptions {
  method?: string
  body?: unknown
  formData?: FormData
  signal?: AbortSignal
  getToken: TokenGetter
}

async function toApiError(response: Response): Promise<ApiError> {
  let code = 'http_error'
  let message = GENERIC_MESSAGE
  let details: ApiErrorDetail[] = []

  try {
    const payload = await response.json()
    if (payload?.error) {
      code = payload.error.code ?? code
      message = payload.error.message ?? message
      details = payload.error.details ?? []
    }
  } catch {
    // A non-envelope body (proxy error, HTML page) must not reach the user.
  }

  if (response.status === 401) {
    message = 'Your session has expired. Please sign in again.'
  }

  return new ApiError(response.status, code, message, details)
}

export async function apiFetch<T>(path: string, options: RequestOptions): Promise<T> {
  const { method = 'GET', body, formData, signal, getToken } = options
  const token = await getToken()

  const headers: Record<string, string> = {}
  if (token) headers.Authorization = `Bearer ${token}`
  if (body !== undefined) headers['Content-Type'] = 'application/json'

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers,
    body: formData ?? (body !== undefined ? JSON.stringify(body) : undefined),
    signal,
  })

  if (!response.ok) {
    throw await toApiError(response)
  }

  if (response.status === 204) {
    return undefined as T
  }

  return (await response.json()) as T
}

export { API_BASE_URL }
