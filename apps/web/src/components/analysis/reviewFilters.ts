import type { ReviewFilters } from '@/lib/api/types'

export interface AppliedFilters {
  minRating: string
  maxRating: string
  after: string
  before: string
}

export const EMPTY_FILTERS: AppliedFilters = { minRating: '', maxRating: '', after: '', before: '' }

export function hasActiveFilters(applied: AppliedFilters): boolean {
  return Boolean(applied.minRating || applied.maxRating || applied.after || applied.before)
}

function toStartOfDay(value: string) {
  return value ? `${value}T00:00:00Z` : undefined
}

function toEndOfDay(value: string) {
  return value ? `${value}T23:59:59Z` : undefined
}

export function toReviewFilters(applied: AppliedFilters): ReviewFilters {
  return {
    minRating: applied.minRating ? Number(applied.minRating) : undefined,
    maxRating: applied.maxRating ? Number(applied.maxRating) : undefined,
    reviewedAfter: toStartOfDay(applied.after),
    reviewedBefore: toEndOfDay(applied.before),
  }
}
