import { screen } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { AnalysisSidebar } from '@/components/layout/AnalysisSidebar'
import { renderWithProviders } from '@/test/utils'

const listAnalysisTargets = vi.fn()
const deleteAnalysisTarget = vi.fn()
vi.mock('@/lib/api/analysisTargets', () => ({
  listAnalysisTargets: (...args: unknown[]) => listAnalysisTargets(...args),
  deleteAnalysisTarget: (...args: unknown[]) => deleteAnalysisTarget(...args),
  renameAnalysisTarget: vi.fn(),
}))

const SOURCE_URL =
  'https://www.google.com/maps/place/Blue+Bottle+Coffee/@37.7823,-122.4074,17z/data=!4m6'

beforeEach(() => {
  listAnalysisTargets.mockResolvedValue([
    {
      id: 'target-1',
      name: 'Blue Bottle Coffee',
      platform: 'google_maps',
      source_url: SOURCE_URL,
      created_at: '2026-09-01T00:00:00Z',
      updated_at: '2026-09-01T00:00:00Z',
    },
  ])
  deleteAnalysisTarget.mockResolvedValue(undefined)
})

describe('AnalysisSidebar', () => {
  it('labels each analysis by name, never by its raw URL', async () => {
    renderWithProviders(<AnalysisSidebar isOpen />)

    expect(await screen.findByText('Blue Bottle Coffee')).toBeInTheDocument()
    expect(screen.queryByText(SOURCE_URL)).not.toBeInTheDocument()
  })

  it('offers a New Analysis action', async () => {
    renderWithProviders(<AnalysisSidebar isOpen />)

    expect(await screen.findByRole('link', { name: /new analysis/i })).toBeInTheDocument()
  })

  it('invites a first analysis when the list is empty', async () => {
    listAnalysisTargets.mockResolvedValue([])
    renderWithProviders(<AnalysisSidebar isOpen />)

    expect(await screen.findByText(/No analyses yet/)).toBeInTheDocument()
  })

  it('exposes per-analysis actions', async () => {
    renderWithProviders(<AnalysisSidebar isOpen />)

    expect(
      await screen.findByRole('button', { name: /actions for Blue Bottle Coffee/i }),
    ).toBeInTheDocument()
  })

  it('never deletes without an explicit confirmation', async () => {
    renderWithProviders(<AnalysisSidebar isOpen />)
    await screen.findByText('Blue Bottle Coffee')

    expect(screen.queryByText(/Delete this analysis\?/)).not.toBeInTheDocument()
    expect(deleteAnalysisTarget).not.toHaveBeenCalled()
  })

  it('marks the open analysis as the current page', async () => {
    renderWithProviders(<AnalysisSidebar isOpen />, { route: '/analysis/target-1' })

    const link = await screen.findByRole('link', { name: 'Blue Bottle Coffee' })
    expect(link).toHaveAttribute('aria-current', 'page')
  })
})
