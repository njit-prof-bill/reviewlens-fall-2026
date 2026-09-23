import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useState } from 'react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import {
  ReviewDatasetDialog,
} from '@/components/analysis/ReviewDatasetDialog'
import { EMPTY_FILTERS, type AppliedFilters } from '@/components/analysis/reviewFilters'
import { renderWithProviders } from '@/test/utils'
import type { ReviewList } from '@/lib/api/types'

const listTargetReviews = vi.fn()
vi.mock('@/lib/api/analysisTargets', () => ({
  listTargetReviews: (...args: unknown[]) => listTargetReviews(...args),
}))

const reviews: ReviewList = {
  items: [
    {
      id: 'review-1',
      review_text: 'Great coffee and friendly staff.',
      rating: 5,
      reviewer_name: 'Kaitlin',
      reviewed_at: '2026-07-01T00:00:00Z',
      source_review_id: 'src-1',
      review_url: null,
    },
  ],
  total: 1,
  limit: 200,
  offset: 0,
}

beforeEach(() => {
  listTargetReviews.mockResolvedValue(reviews)
})

/** Reproduces how AnalysisWorkspace owns applied filters and feeds them back in. */
function ControlledDialog({
  onApplied,
  onOpenChangeSpy,
}: {
  onApplied?: (next: AppliedFilters) => void
  onOpenChangeSpy?: (open: boolean) => void
}) {
  const [open, setOpen] = useState(true)
  const [applied, setApplied] = useState<AppliedFilters>(EMPTY_FILTERS)
  return (
    <>
      <button type="button" onClick={() => setOpen(true)}>
        Reopen
      </button>
      <ReviewDatasetDialog
        targetId="target-1"
        open={open}
        onOpenChange={(next) => {
          setOpen(next)
          onOpenChangeSpy?.(next)
        }}
        applied={applied}
        onApply={(next) => {
          setApplied(next)
          onApplied?.(next)
        }}
      />
    </>
  )
}

describe('ReviewDatasetDialog', () => {
  it('renders nothing when closed', () => {
    renderWithProviders(
      <ReviewDatasetDialog
        targetId="target-1"
        open={false}
        onOpenChange={vi.fn()}
        applied={EMPTY_FILTERS}
        onApply={vi.fn()}
      />,
    )

    expect(screen.queryByText('Review dataset')).not.toBeInTheDocument()
  })

  it('shows the persisted reviews once loaded', async () => {
    renderWithProviders(<ControlledDialog />)

    expect(await screen.findByText('Great coffee and friendly staff.')).toBeInTheDocument()
    expect(screen.getByText('Showing 1 of 1 reviews')).toBeInTheDocument()
  })

  it('does not render pagination controls', async () => {
    renderWithProviders(<ControlledDialog />)

    await screen.findByText('Great coffee and friendly staff.')

    expect(screen.queryByRole('button', { name: /previous/i })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /next/i })).not.toBeInTheDocument()
  })

  it('reports the selected filters to the parent only after OK is pressed', async () => {
    const user = userEvent.setup()
    const onApplied = vi.fn()
    renderWithProviders(<ControlledDialog onApplied={onApplied} />)
    await screen.findByText('Great coffee and friendly staff.')

    await user.selectOptions(screen.getByLabelText('At least'), '4')
    expect(onApplied).not.toHaveBeenCalled()

    await user.click(screen.getByRole('button', { name: /^ok$/i }))

    expect(onApplied).toHaveBeenCalledWith({
      minRating: '4',
      maxRating: '',
      after: '',
      before: '',
    })
  })

  it('reflects an applied filter in the results the next time it opens', async () => {
    const user = userEvent.setup()
    renderWithProviders(<ControlledDialog />)
    await screen.findByText('Great coffee and friendly staff.')

    await user.selectOptions(screen.getByLabelText('At least'), '4')
    await user.click(screen.getByRole('button', { name: /^ok$/i }))
    listTargetReviews.mockClear()

    await user.click(screen.getByRole('button', { name: /^reopen$/i }))

    await waitFor(() => expect(listTargetReviews).toHaveBeenCalled())
    const lastCall = listTargetReviews.mock.calls.at(-1)
    expect(lastCall?.[1].filters.minRating).toBe(4)
  })

  it('closes without applying the pending edit when cancelled', async () => {
    const user = userEvent.setup()
    const onApplied = vi.fn()
    const onOpenChangeSpy = vi.fn()
    renderWithProviders(<ControlledDialog onApplied={onApplied} onOpenChangeSpy={onOpenChangeSpy} />)
    await screen.findByText('Great coffee and friendly staff.')

    await user.selectOptions(screen.getByLabelText('At least'), '4')
    await user.click(screen.getByRole('button', { name: /cancel/i }))

    expect(onApplied).not.toHaveBeenCalled()
    expect(onOpenChangeSpy).toHaveBeenCalledWith(false)
  })
})
