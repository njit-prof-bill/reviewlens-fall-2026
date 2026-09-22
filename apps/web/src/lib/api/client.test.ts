import { afterEach, describe, expect, it, vi } from 'vitest'

import { ApiError, apiDownload, apiFetch } from '@/lib/api/client'

const getToken = async () => 'test-token'

function mockResponse(status: number, body: unknown, isJson = true) {
  vi.stubGlobal(
    'fetch',
    vi.fn(async () => ({
      ok: status >= 200 && status < 300,
      status,
      json: async () => {
        if (!isJson) throw new SyntaxError('Unexpected token <')
        return body
      },
    })),
  )
}

afterEach(() => {
  vi.unstubAllGlobals()
})

async function expectApiError(promise: Promise<unknown>): Promise<ApiError> {
  return promise.then(
    () => {
      throw new Error('Expected the request to fail')
    },
    (error: ApiError) => error,
  )
}

describe('apiFetch', () => {
  it('returns the parsed payload on success', async () => {
    mockResponse(200, { items: [] })

    await expect(apiFetch('/api/v1/analysis-targets', { getToken })).resolves.toEqual({
      items: [],
    })
  })

  it('returns undefined for a 204', async () => {
    mockResponse(204, null)

    await expect(apiFetch('/api/v1/analysis-targets/1', { getToken })).resolves.toBeUndefined()
  })

  it('maps the error envelope onto an ApiError', async () => {
    mockResponse(422, {
      error: {
        code: 'validation_error',
        message: 'The review source is not valid',
        details: [{ field: 'source_url', issue: 'Paste a Google Maps link.' }],
      },
    })

    const error = await expectApiError(apiFetch('/api/v1/analysis-targets', { getToken }))

    expect(error).toBeInstanceOf(ApiError)
    expect(error.status).toBe(422)
    expect(error.fieldIssue('source_url')).toBe('Paste a Google Maps link.')
    expect(error.displayMessage).toBe('Paste a Google Maps link.')
  })

  it('never surfaces a non-envelope body to the user', async () => {
    mockResponse(500, '<html>Traceback: secret internals</html>', false)

    const error = await expectApiError(apiFetch('/api/v1/analysis-targets', { getToken }))

    expect(error.displayMessage).toBe('Something went wrong. Please try again.')
    expect(error.displayMessage).not.toContain('Traceback')
  })

  it('reports an expired session clearly', async () => {
    mockResponse(401, { error: { code: 'http_error', message: 'Not authenticated' } })

    const error = await expectApiError(apiFetch('/api/v1/analysis-targets', { getToken }))

    expect(error.isUnauthorized).toBe(true)
    expect(error.displayMessage).toMatch(/sign in again/i)
  })

  it('flags a denied resource as not found', async () => {
    mockResponse(404, { error: { code: 'not_found', message: 'Analysis target not found' } })

    const error = await expectApiError(apiFetch('/api/v1/analysis-targets/x', { getToken }))

    expect(error.isNotFound).toBe(true)
  })
})

describe('apiDownload', () => {
  it('returns the raw response for a successful download', async () => {
    const response = { ok: true, status: 200, headers: new Headers() }
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(response))

    await expect(apiDownload('/api/v1/analysis-targets/1/exports/reviews.csv', getToken)).resolves.toBe(
      response,
    )
  })

  it('attaches the bearer token when one is available', async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, status: 200, headers: new Headers() })
    vi.stubGlobal('fetch', fetchMock)

    await apiDownload('/api/v1/analysis-targets/1/exports/reviews.csv', getToken)

    const [, init] = fetchMock.mock.calls[0]
    expect(init.headers.Authorization).toBe('Bearer test-token')
  })

  it('maps a failed download onto an ApiError', async () => {
    mockResponse(404, { error: { code: 'not_found', message: 'Analysis target not found' } })

    const error = await expectApiError(
      apiDownload('/api/v1/analysis-targets/1/exports/reviews.csv', getToken),
    )

    expect(error.isNotFound).toBe(true)
  })
})
