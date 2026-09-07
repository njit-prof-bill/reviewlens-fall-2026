import { apiFetch } from '@/lib/api/client'
import type {
  AnalysisTarget,
  AnalysisTargetSummary,
  IngestionRun,
  QAEntry,
  QAEntryList,
  ReviewList,
} from '@/lib/api/types'

type TokenGetter = () => Promise<string | null>

const BASE = '/api/v1/analysis-targets'

export function listAnalysisTargets(getToken: TokenGetter, signal?: AbortSignal) {
  return apiFetch<{ items: AnalysisTarget[] }>(BASE, { getToken, signal }).then(
    (payload) => payload.items,
  )
}

export function getAnalysisTarget(id: string, getToken: TokenGetter, signal?: AbortSignal) {
  return apiFetch<AnalysisTarget>(`${BASE}/${id}`, { getToken, signal })
}

export function createAnalysisTarget(
  input: { name: string; source_url: string },
  getToken: TokenGetter,
) {
  return apiFetch<AnalysisTarget>(BASE, { method: 'POST', body: input, getToken })
}

export function renameAnalysisTarget(id: string, name: string, getToken: TokenGetter) {
  return apiFetch<AnalysisTarget>(`${BASE}/${id}`, {
    method: 'PATCH',
    body: { name },
    getToken,
  })
}

export function deleteAnalysisTarget(id: string, getToken: TokenGetter) {
  return apiFetch<void>(`${BASE}/${id}`, { method: 'DELETE', getToken })
}

export function getTargetSummary(id: string, getToken: TokenGetter, signal?: AbortSignal) {
  return apiFetch<AnalysisTargetSummary>(`${BASE}/${id}/summary`, { getToken, signal })
}

export function listTargetReviews(
  id: string,
  options: { limit: number; offset: number },
  getToken: TokenGetter,
  signal?: AbortSignal,
) {
  const query = new URLSearchParams({
    limit: String(options.limit),
    offset: String(options.offset),
  })
  return apiFetch<ReviewList>(`${BASE}/${id}/reviews?${query}`, { getToken, signal })
}

/** Primary ingestion path: collect reviews from the target's source URL. */
export function startUrlIngestion(id: string, getToken: TokenGetter) {
  return apiFetch<IngestionRun>(`${BASE}/${id}/ingestions`, { method: 'POST', getToken })
}

/** Recovery path used when the live review source is unavailable. */
export function startFileImport(id: string, file: File, getToken: TokenGetter) {
  const formData = new FormData()
  formData.append('file', file)
  return apiFetch<IngestionRun>(`${BASE}/${id}/ingestions/imports`, {
    method: 'POST',
    formData,
    getToken,
  })
}

export function getIngestionRun(runId: string, getToken: TokenGetter, signal?: AbortSignal) {
  return apiFetch<IngestionRun>(`/api/v1/ingestion-runs/${runId}`, { getToken, signal })
}

export function listTargetQuestions(
  id: string,
  getToken: TokenGetter,
  signal?: AbortSignal,
) {
  return apiFetch<QAEntryList>(`${BASE}/${id}/questions`, { getToken, signal })
}

export function askTargetQuestion(id: string, question: string, getToken: TokenGetter) {
  return apiFetch<QAEntry>(`${BASE}/${id}/questions`, {
    method: 'POST',
    body: { question },
    getToken,
  })
}
