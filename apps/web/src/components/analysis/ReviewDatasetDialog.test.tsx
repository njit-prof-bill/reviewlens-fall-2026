import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { ReviewDatasetDialog } from '@/components/analysis/ReviewDatasetDialog'
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

describe('ReviewDatasetDialog', () => {
  it('renders nothing when closed', () => {
    renderWithProviders(
      <ReviewDatasetDialog targetId="target-1" open={false} onOpenChange={vi.fn()} />,
    )

    expect(screen.queryByText('Review dataset')).not.toBeInTheDocument()
  })

  it('shows the persisted reviews once loaded', async () => {
    renderWithProviders(
      <ReviewDatasetDialog targetId="target-1" open onOpenChange={vi.fn()} />,
    )

    expect(await screen.findByText('Great coffee and friendly staff.')).toBeInTheDocument()
    expect(screen.getByText('Showing 1 of 1 reviews')).toBeInTheDocument()
  })

  it('does not render pagination controls', async () => {
    renderWithProviders(
      <ReviewDatasetDialog targetId="target-1" open onOpenChange={vi.fn()} />,
    )

    await screen.findByText('Great coffee and friendly staff.')

    expect(screen.queryByRole('button', { name: /previous/i })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /next/i })).not.toBeInTheDocument()
  })

  it('applies the selected filters only after OK is pressed', async () => {
    const user = userEvent.setup()
    renderWithProviders(
      <ReviewDatasetDialog targetId="target-1" open onOpenChange={vi.fn()} />,
    )
    await screen.findByText('Great coffee and friendly staff.')
    listTargetReviews.mockClear()

    await user.selectOptions(screen.getByLabelText('At least'), '4')
    expect(listTargetReviews).not.toHaveBeenCalled()

    await user.click(screen.getByRole('button', { name: /^ok$/i }))

    await waitFor(() => expect(listTargetReviews).toHaveBeenCalled())
    const lastCall = listTargetReviews.mock.calls.at(-1)
    expect(lastCall?.[1].filters.minRating).toBe(4)
  })

  it('closes without applying the pending edit when cancelled', async () => {
    const user = userEvent.setup()
    const onOpenChange = vi.fn()
    renderWithProviders(
      <ReviewDatasetDialog targetId="target-1" open onOpenChange={onOpenChange} />,
    )
    await screen.findByText('Great coffee and friendly staff.')

    await user.selectOptions(screen.getByLabelText('At least'), '4')
    await user.click(screen.getByRole('button', { name: /cancel/i }))

    expect(onOpenChange).toHaveBeenCalledWith(false)
  })
})
