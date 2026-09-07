import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { ReviewQANotebook } from '@/components/analysis/ReviewQANotebook'
import { ApiError } from '@/lib/api/client'
import { renderWithProviders } from '@/test/utils'

const listTargetQuestions = vi.fn()
const askTargetQuestion = vi.fn()

vi.mock('@/lib/api/analysisTargets', () => ({
  listTargetQuestions: (...args: unknown[]) => listTargetQuestions(...args),
  askTargetQuestion: (...args: unknown[]) => askTargetQuestion(...args),
}))

beforeEach(() => {
  listTargetQuestions.mockResolvedValue({
    items: [
      {
        id: 'question-1',
        analysis_target_id: 'target-1',
        question: 'What do customers like?',
        answer: 'Customers repeatedly praise the friendly staff.',
        result_kind: 'grounded',
        provider: 'openai',
        model: 'gpt-4.1-mini',
        context_review_count: 18,
        created_at: '2026-09-05T12:00:00Z',
        evidence: [
          {
            review_id: 'review-1',
            excerpt: 'The staff made us feel welcome.',
            rating: 5,
            reviewer_name: 'Jordan',
            reviewed_at: null,
          },
        ],
      },
      {
        id: 'question-2',
        analysis_target_id: 'target-1',
        question: 'What is the weather?',
        answer: 'I can only answer questions about this review dataset.',
        result_kind: 'out_of_scope',
        provider: 'openai',
        model: 'gpt-4.1-mini',
        context_review_count: 18,
        created_at: '2026-09-05T12:01:00Z',
        evidence: [],
      },
    ],
  })
  askTargetQuestion.mockResolvedValue({
    id: 'question-3',
    analysis_target_id: 'target-1',
  })
})

describe('ReviewQANotebook', () => {
  it('renders persisted grounded evidence and a scope refusal', async () => {
    renderWithProviders(
      <ReviewQANotebook targetId="target-1" targetName="Blue Bottle" enabled />,
    )

    expect(await screen.findByText(/friendly staff/)).toBeInTheDocument()
    expect(screen.getByText(/staff made us feel welcome/)).toBeInTheDocument()
    expect(screen.getByText('Outside this analysis')).toBeInTheDocument()
  })

  it('submits a trimmed question for the active target', async () => {
    const user = userEvent.setup()
    renderWithProviders(
      <ReviewQANotebook targetId="target-1" targetName="Blue Bottle" enabled />,
    )

    await user.type(
      screen.getByLabelText('Ask about Blue Bottle'),
      '  What complaints appear repeatedly?  ',
    )
    await user.click(screen.getByRole('button', { name: 'Ask question' }))

    expect(askTargetQuestion).toHaveBeenCalledWith(
      'target-1',
      'What complaints appear repeatedly?',
      expect.any(Function),
    )
  })

  it('shows an empty-target gate instead of the question form', () => {
    renderWithProviders(
      <ReviewQANotebook targetId="target-1" targetName="Empty Cafe" enabled={false} />,
    )

    expect(screen.getByText('Reviews required')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Ask question' })).not.toBeInTheDocument()
  })

  it('shows a safe API error and preserves the question for retry', async () => {
    const user = userEvent.setup()
    askTargetQuestion.mockRejectedValue(
      new ApiError(503, 'service_unavailable', 'The AI service is temporarily unavailable.'),
    )
    renderWithProviders(
      <ReviewQANotebook targetId="target-1" targetName="Blue Bottle" enabled />,
    )

    const input = screen.getByLabelText('Ask about Blue Bottle')
    await user.type(input, 'What do customers like?')
    await user.click(screen.getByRole('button', { name: 'Ask question' }))

    expect(await screen.findByText(/temporarily unavailable/)).toBeInTheDocument()
    expect(input).toHaveValue('What do customers like?')
  })
})