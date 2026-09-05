import { screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { ReviewPreviewTable } from '@/components/analysis/ReviewPreviewTable'
import { renderWithProviders } from '@/test/utils'
import type { ReviewList } from '@/lib/api/types'

const reviews: ReviewList = {
  items: [
    {
      id: 'r1',
      review_text: 'The pour over here is consistently excellent.',
      rating: 5,
      reviewer_name: 'Dana Whitfield',
      reviewed_at: '2026-07-02T14:31:00Z',
      source_review_id: 'gm-001',
      review_url: null,
    },
    {
      id: 'r2',
      review_text: 'Great espresso but the seating is limited.',
      rating: 4,
      reviewer_name: null,
      reviewed_at: null,
      source_review_id: 'gm-002',
      review_url: null,
    },
  ],
  total: 18,
  limit: 5,
  offset: 0,
}

describe('ReviewPreviewTable', () => {
  it('renders each review with its rating and text', () => {
    renderWithProviders(<ReviewPreviewTable reviews={reviews} isLoading={false} />)

    expect(screen.getByText(/pour over here is consistently excellent/)).toBeInTheDocument()
    expect(screen.getByText('Dana Whitfield')).toBeInTheDocument()
    expect(screen.getByText('5.0')).toBeInTheDocument()
    expect(screen.getByText('Showing 2 of 18 reviews')).toBeInTheDocument()
  })

  it('falls back to Anonymous when no reviewer name was captured', () => {
    renderWithProviders(<ReviewPreviewTable reviews={reviews} isLoading={false} />)

    expect(screen.getByText('Anonymous')).toBeInTheDocument()
  })

  it('renders an empty state rather than a bare table', () => {
    renderWithProviders(
      <ReviewPreviewTable
        reviews={{ items: [], total: 0, limit: 5, offset: 0 }}
        isLoading={false}
      />,
    )

    expect(screen.getByText(/Reviews will appear here/)).toBeInTheDocument()
    expect(screen.queryByRole('table')).not.toBeInTheDocument()
  })

  it('offers View more only when more reviews exist', () => {
    const { rerender } = renderWithProviders(
      <ReviewPreviewTable reviews={reviews} isLoading={false} canViewMore />,
    )
    expect(screen.getByRole('button', { name: /view more reviews/i })).toBeInTheDocument()

    rerender(<ReviewPreviewTable reviews={reviews} isLoading={false} canViewMore={false} />)
    expect(screen.queryByRole('button', { name: /view more reviews/i })).not.toBeInTheDocument()
  })
})
