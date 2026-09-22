import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { SaveAsAnalysisDialog } from '@/components/analysis/SaveAsAnalysisDialog'
import { renderWithProviders } from '@/test/utils'
import type { AnalysisTarget } from '@/lib/api/types'

const copyAnalysisTarget = vi.fn()
vi.mock('@/lib/api/analysisTargets', () => ({
  copyAnalysisTarget: (...args: unknown[]) => copyAnalysisTarget(...args),
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
  copyAnalysisTarget.mockResolvedValue({ ...target, id: 'target-2', name: 'Blue Bottle Coffee Copy' })
})

describe('SaveAsAnalysisDialog', () => {
  it('renders nothing when no analysis is selected', () => {
    renderWithProviders(
      <SaveAsAnalysisDialog target={null} onClose={vi.fn()} onCopied={vi.fn()} />,
    )

    expect(screen.queryByText('Save as new analysis')).not.toBeInTheDocument()
  })

  it('suggests a name derived from the source analysis', () => {
    renderWithProviders(
      <SaveAsAnalysisDialog target={target} onClose={vi.fn()} onCopied={vi.fn()} />,
    )

    expect(screen.getByLabelText('Name')).toHaveValue('Blue Bottle Coffee Copy')
  })

  it('states that Q&A history starts empty', () => {
    renderWithProviders(
      <SaveAsAnalysisDialog target={target} onClose={vi.fn()} onCopied={vi.fn()} />,
    )

    expect(screen.getByText(/Q&A history starts empty/i)).toBeInTheDocument()
  })

  it('creates a copy under the entered name and reports the new analysis', async () => {
    const user = userEvent.setup()
    const onClose = vi.fn()
    const onCopied = vi.fn()
    renderWithProviders(
      <SaveAsAnalysisDialog target={target} onClose={onClose} onCopied={onCopied} />,
    )

    await user.clear(screen.getByLabelText('Name'))
    await user.type(screen.getByLabelText('Name'), 'Mint Plaza Copy')
    await user.click(screen.getByRole('button', { name: /save as/i }))

    await waitFor(() => expect(copyAnalysisTarget).toHaveBeenCalledWith('target-1', 'Mint Plaza Copy', expect.any(Function)))
    expect(onClose).toHaveBeenCalled()
    expect(onCopied).toHaveBeenCalledWith({ ...target, id: 'target-2', name: 'Blue Bottle Coffee Copy' })
  })

  it('does not submit a blank name', async () => {
    const user = userEvent.setup()
    renderWithProviders(
      <SaveAsAnalysisDialog target={target} onClose={vi.fn()} onCopied={vi.fn()} />,
    )

    await user.clear(screen.getByLabelText('Name'))

    expect(screen.getByRole('button', { name: /save as/i })).toBeDisabled()
    expect(copyAnalysisTarget).not.toHaveBeenCalled()
  })

  it('cancels without copying', async () => {
    const user = userEvent.setup()
    const onClose = vi.fn()
    renderWithProviders(
      <SaveAsAnalysisDialog target={target} onClose={onClose} onCopied={vi.fn()} />,
    )

    await user.click(screen.getByRole('button', { name: /cancel/i }))

    expect(copyAnalysisTarget).not.toHaveBeenCalled()
    expect(onClose).toHaveBeenCalled()
  })
})
