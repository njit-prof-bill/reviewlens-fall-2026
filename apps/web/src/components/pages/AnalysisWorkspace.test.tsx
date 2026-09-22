import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { AnalysisWorkspace } from '@/components/pages/AnalysisWorkspace'
import { ApiError } from '@/lib/api/client'
import { renderWithProviders } from '@/test/utils'

const getAnalysisTarget = vi.fn()
const getTargetSummary = vi.fn()
const listTargetReviews = vi.fn()
const listTargetQuestions = vi.fn()
const exportTargetReviewsCsv = vi.fn()
const exportTargetAnalysisMarkdown = vi.fn()

vi.mock('@/lib/api/analysisTargets', () => ({
  getAnalysisTarget: (...args: unknown[]) => getAnalysisTarget(...args),
  getTargetSummary: (...args: unknown[]) => getTargetSummary(...args),
  listTargetReviews: (...args: unknown[]) => listTargetReviews(...args),
  listTargetQuestions: (...args: unknown[]) => listTargetQuestions(...args),
  askTargetQuestion: vi.fn(),
  getIngestionRun: vi.fn(),
  startUrlIngestion: vi.fn(),
  startFileImport: vi.fn(),
  exportTargetReviewsCsv: (...args: unknown[]) => exportTargetReviewsCsv(...args),
  exportTargetAnalysisMarkdown: (...args: unknown[]) => exportTargetAnalysisMarkdown(...args),
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
  listTargetQuestions.mockResolvedValue({ items: [] })
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
    expect(await screen.findByText('Ask the Reviews')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /refresh reviews/i })).toBeInTheDocument()
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

  it('downloads the review dataset as CSV using the server-provided filename', async () => {
    const user = userEvent.setup()
    const blob = new Blob(['rating,review_text'], { type: 'text/csv' })
    exportTargetReviewsCsv.mockResolvedValue({
      blob: async () => blob,
      headers: new Headers({
        'content-disposition': 'attachment; filename="blue-bottle-coffee-reviews.csv"',
      }),
    })
    const createObjectURL = vi.fn(() => 'blob:mock-url')
    const revokeObjectURL = vi.fn()
    vi.stubGlobal('URL', { ...URL, createObjectURL, revokeObjectURL })
    const clickSpy = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {})

    renderWithProviders(<AnalysisWorkspace />)
    await user.click(await screen.findByRole('button', { name: /export csv/i }))

    await waitFor(() =>
      expect(exportTargetReviewsCsv).toHaveBeenCalledWith('target-1', expect.any(Function)),
    )
    expect(createObjectURL).toHaveBeenCalledWith(blob)
    expect(clickSpy).toHaveBeenCalled()

    clickSpy.mockRestore()
    vi.unstubAllGlobals()
  })

  it('downloads the analysis as Markdown', async () => {
    const user = userEvent.setup()
    const blob = new Blob(['# Blue Bottle Coffee'], { type: 'text/markdown' })
    exportTargetAnalysisMarkdown.mockResolvedValue({
      blob: async () => blob,
      headers: new Headers({
        'content-disposition': 'attachment; filename="blue-bottle-coffee-analysis.md"',
      }),
    })
    vi.stubGlobal('URL', {
      ...URL,
      createObjectURL: vi.fn(() => 'blob:mock-url'),
      revokeObjectURL: vi.fn(),
    })
    const clickSpy = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {})

    renderWithProviders(<AnalysisWorkspace />)
    await user.click(await screen.findByRole('button', { name: /export markdown/i }))

    await waitFor(() =>
      expect(exportTargetAnalysisMarkdown).toHaveBeenCalledWith('target-1', expect.any(Function)),
    )

    clickSpy.mockRestore()
    vi.unstubAllGlobals()
  })

  it('opens the review dataset dialog for browsing and filtering', async () => {
    listTargetReviews.mockResolvedValue({
      items: [
        {
          id: 'review-1',
          review_text: 'Great coffee.',
          rating: 5,
          reviewer_name: 'Kaitlin',
          reviewed_at: '2026-07-01T00:00:00Z',
          source_review_id: 'src-1',
          review_url: null,
        },
      ],
      total: 1,
      limit: 5,
      offset: 0,
    })
    const user = userEvent.setup()

    renderWithProviders(<AnalysisWorkspace />)
    await user.click(await screen.findByRole('button', { name: /browse and filter reviews/i }))

    expect(await screen.findByText('Review dataset')).toBeInTheDocument()
  })
})
