export interface AnalysisTarget {
  id: string
  name: string
  platform: string
  source_url: string
  created_at: string
  updated_at: string
}

export type IngestionStatus = 'pending' | 'processing' | 'succeeded' | 'partial' | 'failed'

export const TERMINAL_STATUSES: IngestionStatus[] = ['succeeded', 'partial', 'failed']

export function isTerminal(status: IngestionStatus | undefined): boolean {
  return status !== undefined && TERMINAL_STATUSES.includes(status)
}

export interface IngestionRun {
  id: string
  analysis_target_id: string
  status: IngestionStatus
  source_kind: 'url_fetch' | 'file_import'
  reviews_ingested: number
  reviews_rejected: number
  reviews_duplicate: number
  rejection_reasons: Record<string, number> | null
  error_code: string | null
  error_message: string | null
  started_at: string | null
  completed_at: string | null
  created_at: string
}

export interface Review {
  id: string
  review_text: string
  rating: number
  reviewer_name: string | null
  reviewed_at: string | null
  source_review_id: string | null
  review_url: string | null
}

export interface ReviewList {
  items: Review[]
  total: number
  limit: number
  offset: number
}

export interface AnalysisTargetSummary {
  entity_name: string
  platform: string
  source_url: string
  reviews_collected: number
  average_rating: number | null
  earliest_review: string | null
  latest_review: string | null
  latest_run: IngestionRun | null
}

export type QAResultKind = 'grounded' | 'insufficient_evidence' | 'out_of_scope'

export interface QAEvidence {
  review_id: string | null
  excerpt: string
  rating: number | null
  reviewer_name: string | null
  reviewed_at: string | null
}

export interface QAEntry {
  id: string
  analysis_target_id: string
  question: string
  answer: string
  result_kind: QAResultKind
  provider: string
  model: string
  context_review_count: number
  created_at: string
  evidence: QAEvidence[]
}

export interface QAEntryList {
  items: QAEntry[]
}

export const PLATFORM_LABELS: Record<string, string> = {
  google_maps: 'Google Maps',
}

export function platformLabel(platform: string): string {
  return PLATFORM_LABELS[platform] ?? platform
}
