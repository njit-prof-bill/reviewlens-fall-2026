import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { NewAnalysis } from '@/components/pages/NewAnalysis'
import { renderWithProviders } from '@/test/utils'

const navigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>('react-router-dom')
  return { ...actual, useNavigate: () => navigate }
})

const createAnalysisTarget = vi.fn()
const startUrlIngestion = vi.fn()
vi.mock('@/lib/api/analysisTargets', () => ({
  createAnalysisTarget: (...args: unknown[]) => createAnalysisTarget(...args),
  startUrlIngestion: (...args: unknown[]) => startUrlIngestion(...args),
}))

const PLACE_URL =
  'https://www.google.com/maps/place/Blue+Bottle+Coffee/@37.7823,-122.4074,17z'

beforeEach(() => {
  createAnalysisTarget.mockResolvedValue({ id: 'target-1', name: 'Blue Bottle Coffee' })
  startUrlIngestion.mockResolvedValue({ id: 'run-1', status: 'pending' })
})

describe('NewAnalysis', () => {
  it('shows only the URL field and the analyze action', () => {
    renderWithProviders(<NewAnalysis />)

    expect(screen.getByLabelText('Google Maps URL')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /analyze reviews/i })).toBeInTheDocument()
    expect(screen.queryByRole('table')).not.toBeInTheDocument()
  })

  it('rejects an unsupported URL without calling the API', async () => {
    const user = userEvent.setup()
    renderWithProviders(<NewAnalysis />)

    await user.type(screen.getByLabelText('Google Maps URL'), 'https://www.yelp.com/biz/x')
    await user.click(screen.getByRole('button', { name: /analyze reviews/i }))

    expect(await screen.findByRole('alert')).toHaveTextContent(/Google Maps links only/)
    expect(createAnalysisTarget).not.toHaveBeenCalled()
  })

  it('rejects an empty submission', async () => {
    const user = userEvent.setup()
    renderWithProviders(<NewAnalysis />)

    await user.click(screen.getByRole('button', { name: /analyze reviews/i }))

    expect(await screen.findByRole('alert')).toBeInTheDocument()
    expect(createAnalysisTarget).not.toHaveBeenCalled()
  })

  it('creates the target, starts collection, and opens the workspace', async () => {
    const user = userEvent.setup()
    renderWithProviders(<NewAnalysis />)

    await user.type(screen.getByLabelText('Google Maps URL'), PLACE_URL)
    await user.click(screen.getByRole('button', { name: /analyze reviews/i }))

    await waitFor(() => expect(createAnalysisTarget).toHaveBeenCalled())
    expect(createAnalysisTarget.mock.calls[0][0]).toEqual({
      name: 'Blue Bottle Coffee',
      source_url: PLACE_URL,
    })
    await waitFor(() => expect(startUrlIngestion).toHaveBeenCalled())
    expect(navigate).toHaveBeenCalledWith('/analysis/target-1?run=run-1')
  })

  it('surfaces a server validation message without exposing internals', async () => {
    const { ApiError } = await import('@/lib/api/client')
    createAnalysisTarget.mockRejectedValue(
      new ApiError(422, 'validation_error', 'The review source is not valid', [
        { field: 'source_url', issue: 'That Google link is not a Google Maps place.' },
      ]),
    )
    const user = userEvent.setup()
    renderWithProviders(<NewAnalysis />)

    await user.type(screen.getByLabelText('Google Maps URL'), PLACE_URL)
    await user.click(screen.getByRole('button', { name: /analyze reviews/i }))

    expect(await screen.findByRole('alert')).toHaveTextContent(
      /not a Google Maps place/,
    )
  })
})
