import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { DeleteAnalysisDialog } from '@/components/analysis/DeleteAnalysisDialog'
import { renderWithProviders } from '@/test/utils'
import type { AnalysisTarget } from '@/lib/api/types'

const deleteAnalysisTarget = vi.fn()
vi.mock('@/lib/api/analysisTargets', () => ({
  deleteAnalysisTarget: (...args: unknown[]) => deleteAnalysisTarget(...args),
}))

const target: AnalysisTarget = {
  id: 'target-1',
  name: 'Blue Bottle Coffee',
  platform: 'google_maps',
  source_url: 'https://www.google.com/maps/place/Blue+Bottle+Coffee',
  created_at: '2026-09-01T00:00:00Z',
  updated_at: '2026-09-01T00:00:00Z',
}

beforeEach(() => {
  deleteAnalysisTarget.mockResolvedValue(undefined)
})

describe('DeleteAnalysisDialog', () => {
  it('names what will be destroyed and warns it is permanent', () => {
    renderWithProviders(<DeleteAnalysisDialog target={target} onClose={vi.fn()} />)

    expect(screen.getByText('Delete this analysis?')).toBeInTheDocument()
    expect(screen.getByText(/Blue Bottle Coffee/)).toBeInTheDocument()
    expect(screen.getByText(/cannot be undone/i)).toBeInTheDocument()
  })

  it('deletes nothing until the action is confirmed', () => {
    renderWithProviders(<DeleteAnalysisDialog target={target} onClose={vi.fn()} />)

    expect(deleteAnalysisTarget).not.toHaveBeenCalled()
  })

  it('deletes on confirmation and reports which analysis went away', async () => {
    const user = userEvent.setup()
    const onClose = vi.fn()
    const onDeleted = vi.fn()
    renderWithProviders(
      <DeleteAnalysisDialog target={target} onClose={onClose} onDeleted={onDeleted} />,
    )

    await user.click(screen.getByRole('button', { name: /^delete$/i }))

    await waitFor(() => expect(deleteAnalysisTarget).toHaveBeenCalledTimes(1))
    expect(deleteAnalysisTarget.mock.calls[0][0]).toBe('target-1')
    await waitFor(() => expect(onDeleted).toHaveBeenCalledWith('target-1'))
    expect(onClose).toHaveBeenCalled()
  })

  it('cancels without deleting', async () => {
    const user = userEvent.setup()
    const onClose = vi.fn()
    renderWithProviders(<DeleteAnalysisDialog target={target} onClose={onClose} />)

    await user.click(screen.getByRole('button', { name: /cancel/i }))

    expect(deleteAnalysisTarget).not.toHaveBeenCalled()
    await waitFor(() => expect(onClose).toHaveBeenCalled())
  })

  it('renders nothing when no analysis is selected', () => {
    renderWithProviders(<DeleteAnalysisDialog target={null} onClose={vi.fn()} />)

    expect(screen.queryByText('Delete this analysis?')).not.toBeInTheDocument()
  })
})
