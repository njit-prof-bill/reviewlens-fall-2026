import type { IngestionStatus } from '@/lib/api/types'

export function formatReviewDate(value: string | null | undefined): string {
  if (!value) return '—'
  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) return '—'
  return parsed.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

export function formatRating(value: number | null | undefined): string {
  return value === null || value === undefined ? '—' : value.toFixed(1)
}

export function formatDateRange(earliest: string | null, latest: string | null): string {
  if (!earliest && !latest) return '—'
  return `${formatReviewDate(earliest)} – ${formatReviewDate(latest)}`
}

/**
 * "Never ingested" is deliberately distinct from "failed" so an untouched
 * analysis never reads as a failure.
 */
export type DisplayState = 'not-started' | 'processing' | 'complete' | 'partial' | 'failed'

export function toDisplayState(status: IngestionStatus | null | undefined): DisplayState {
  switch (status) {
    case 'pending':
    case 'processing':
      return 'processing'
    case 'succeeded':
      return 'complete'
    case 'partial':
      return 'partial'
    case 'failed':
      return 'failed'
    default:
      return 'not-started'
  }
}

export const DISPLAY_STATE_LABELS: Record<DisplayState, string> = {
  'not-started': 'Not yet collected',
  processing: 'Collecting reviews',
  complete: 'Complete',
  partial: 'Partial',
  failed: 'Failed',
}
