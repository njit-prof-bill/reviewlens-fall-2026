import { screen } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { AnalysisWorkspace } from '@/components/pages/AnalysisWorkspace'
import { ApiError } from '@/lib/api/client'
import { renderWithProviders } from '@/test/utils'

const getAnalysisTarget = vi.fn()
const getTargetSummary = vi.fn()
const listTargetReviews = vi.fn()

vi.mock('@/lib/api/analysisTargets', () => ({
  getAnalysisTarget: (...args: unknown[]) => getAnalysisTarget(...args),
  getTargetSummary: (...args: unknown[]) => getTargetSummary(...args),
  listTargetReviews: (...args: unknown[]) => listTargetReviews(...args),
  getIngestionRun: vi.fn(),
  startUrlIngestion: vi.fn(),
  startFileImport: vi.fn(),
}))

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>('react-router-dom')
  return { ...actual, useParams: () => ({ targetId: 'target-1' }) }
})

beforeEach(() => {
  getAnalysisTarget.mockResolvedValue({
    id: 'target-1',
    name: 'Blue Bottle Coffee',
    platform: 'google_maps',
    source_url: 'https://www.google.com/maps/place/Blue+Bottle+Coffee',
    created_at: '2026-09-01T00:00:00Z',
    updated_at: '2026-09-01T00:00:00Z',
  })
  getTargetSummary.mockResolvedValue({
    entity_name: 'Blue Bottle Coffee',
    platform: 'google_maps',
    source_url: 'https://www.google.com/maps/place/Blue+Bottle+Coffee',
    reviews_collected: 18,
    average_rating: 4.3,
    earliest_review: '2026-04-08T00:00:00Z',
    latest_review: '2026-07-02T00:00:00Z',
    latest_run: null,
  })
  listTargetReviews.mockResolvedValue({ items: [], total: 0, limit: 5, offset: 0 })
})

describe('AnalysisWorkspace', () => {
  it('identifies the active target and its scope', async () => {
    renderWithProviders(<AnalysisWorkspace />)

    expect(await screen.findByRole('heading', { name: 'Blue Bottle Coffee' })).toBeInTheDocument()
    expect(await screen.findByText('Current Analysis Scope')).toBeInTheDocument()
    expect(
      await screen.findByText(/answer questions only from this dataset/i),
    ).toBeInTheDocument()
  })

  it('shows the notebook steps and an ingestion action', async () => {
    renderWithProviders(<AnalysisWorkspace />)

    expect(await screen.findByText('Ingestion Summary')).toBeInTheDocument()
    expect(await screen.findByText('Review Preview')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /analyze reviews/i })).toBeInTheDocument()
  })

  it('denies a target owned by another account without leaking anything', async () => {
    getAnalysisTarget.mockRejectedValue(
      new ApiError(404, 'not_found', 'Analysis target not found'),
    )

    renderWithProviders(<AnalysisWorkspace />)

    expect(await screen.findByText('Analysis not available')).toBeInTheDocument()
    expect(screen.getByText(/belongs to another account/i)).toBeInTheDocument()
    expect(screen.queryByText('Current Analysis Scope')).not.toBeInTheDocument()
  })
})
