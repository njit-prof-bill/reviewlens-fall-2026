import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'

import { ImportReviewsDialog } from '@/components/analysis/ImportReviewsDialog'
import { renderWithProviders } from '@/test/utils'

function setup(onImport = vi.fn().mockResolvedValue({ id: 'run-1' })) {
  renderWithProviders(
    <ImportReviewsDialog
      open
      onOpenChange={vi.fn()}
      onImport={onImport}
      isImporting={false}
    />,
  )
  return onImport
}

describe('ImportReviewsDialog', () => {
  it('rejects an unsupported file type before uploading', async () => {
    const user = userEvent.setup()
    const onImport = setup()

    const file = new File(['%PDF-1.4'], 'reviews.pdf', { type: 'application/pdf' })
    await user.upload(screen.getByLabelText(/review file/i), file)
    await user.click(screen.getByRole('button', { name: /import reviews/i }))

    expect(await screen.findByRole('alert')).toHaveTextContent(/\.csv or \.json/)
    expect(onImport).not.toHaveBeenCalled()
  })

  it('requires a file to be chosen', async () => {
    const user = userEvent.setup()
    const onImport = setup()

    await user.click(screen.getByRole('button', { name: /import reviews/i }))

    expect(await screen.findByRole('alert')).toBeInTheDocument()
    expect(onImport).not.toHaveBeenCalled()
  })

  it('uploads a supported file', async () => {
    const user = userEvent.setup()
    const onImport = setup()

    const file = new File(['review_text,rating\nGood,5\n'], 'reviews.csv', {
      type: 'text/csv',
    })
    await user.upload(screen.getByLabelText(/review file/i), file)
    await user.click(screen.getByRole('button', { name: /import reviews/i }))

    await waitFor(() => expect(onImport).toHaveBeenCalledWith(file))
  })

  it('shows a safe message when the server rejects the file', async () => {
    const { ApiError } = await import('@/lib/api/client')
    const user = userEvent.setup()
    const onImport = setup(
      vi.fn().mockRejectedValue(
        new ApiError(422, 'validation_error', 'The review file is not valid', [
          { field: 'file', issue: 'Upload a .csv or .json file.' },
        ]),
      ),
    )

    const file = new File(['bad'], 'reviews.csv', { type: 'text/csv' })
    await user.upload(screen.getByLabelText(/review file/i), file)
    await user.click(screen.getByRole('button', { name: /import reviews/i }))

    await waitFor(() => expect(onImport).toHaveBeenCalled())
    expect(await screen.findByRole('alert')).toHaveTextContent(/Upload a \.csv or \.json file/)
  })
})
