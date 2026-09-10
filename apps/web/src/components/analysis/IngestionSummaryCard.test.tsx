import { screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { IngestionSummaryCard } from '@/components/analysis/IngestionSummaryCard'
import { renderWithProviders } from '@/test/utils'
import type { AnalysisTargetSummary, IngestionRun, IngestionStatus } from '@/lib/api/types'

function run(status: IngestionStatus, overrides: Partial<IngestionRun> = {}): IngestionRun {
  return {
    id: 'run-1',
    analysis_target_id: 'target-1',
    status,
    source_kind: 'url_fetch',
    reviews_ingested: 18,
    reviews_rejected: 0,
    rejection_reasons: null,
    error_code: null,
    error_message: null,
    started_at: '2026-09-01T00:00:00Z',
    completed_at: '2026-09-01T00:01:00Z',
    created_at: '2026-09-01T00:00:00Z',
    ...overrides,
  }
}

function summary(latest: IngestionRun | null, overrides: Partial<AnalysisTargetSummary> = {}) {
  return {
    entity_name: 'Blue Bottle Coffee',
    platform: 'google_maps',
    source_url: 'https://www.google.com/maps/place/Blue+Bottle+Coffee',
    reviews_collected: latest ? 18 : 0,
    average_rating: latest ? 4.3 : null,
    earliest_review: latest ? '2026-04-08T00:00:00Z' : null,
    latest_review: latest ? '2026-07-02T00:00:00Z' : null,
    latest_run: latest,
    ...overrides,
  } satisfies AnalysisTargetSummary
}

describe('IngestionSummaryCard', () => {
  it('distinguishes never-collected from failed', () => {
    renderWithProviders(<IngestionSummaryCard summary={summary(null)} isLoading={false} />)

    expect(screen.getByText('Not yet collected')).toBeInTheDocument()
    expect(screen.queryByText('Failed')).not.toBeInTheDocument()
    expect(screen.getByText(/No reviews have been collected/)).toBeInTheDocument()
  })

  it('renders the collected statistics on success', () => {
    renderWithProviders(
      <IngestionSummaryCard summary={summary(run('succeeded'))} isLoading={false} />,
    )

    expect(screen.getByText('Complete')).toBeInTheDocument()
    expect(screen.getByText('18')).toBeInTheDocument()
    expect(screen.getByText('4.3')).toBeInTheDocument()
    expect(screen.getByText('Blue Bottle Coffee')).toBeInTheDocument()
    expect(screen.getByText('Google Maps')).toBeInTheDocument()
  })

  it('explains a partial result with both counts', () => {
    renderWithProviders(
      <IngestionSummaryCard
        summary={summary(
          run('partial', {
            reviews_ingested: 15,
            reviews_rejected: 3,
            rejection_reasons: {
              missing_review_text: 1,
              missing_or_invalid_rating: 2,
            },
          }),
        )}
        isLoading={false}
      />,
    )

    expect(screen.getByText('Partial')).toBeInTheDocument()
    expect(screen.getByText(/15 collected and 3 skipped/)).toBeInTheDocument()
    expect(screen.getByText(/1 missing review text/)).toBeInTheDocument()
    expect(screen.getByText(/2 missing or invalid rating/)).toBeInTheDocument()
  })

  it('shows the user-safe failure message and no technical detail', () => {
    renderWithProviders(
      <IngestionSummaryCard
        summary={summary(
          run('failed', {
            reviews_ingested: 0,
            error_code: 'provider_unavailable',
            error_message: 'The review service is temporarily unavailable. Please try again later.',
          }),
          { reviews_collected: 0, average_rating: null },
        )}
        isLoading={false}
      />,
    )

    expect(screen.getByText('Failed')).toBeInTheDocument()
    expect(screen.getByText(/temporarily unavailable/)).toBeInTheDocument()
    expect(screen.queryByText(/Traceback/)).not.toBeInTheDocument()
  })

  it('shows a collecting state while a run is in flight', () => {
    renderWithProviders(
      <IngestionSummaryCard summary={summary(run('processing'))} isLoading={false} />,
    )

    expect(screen.getByText('Collecting reviews')).toBeInTheDocument()
  })
})
