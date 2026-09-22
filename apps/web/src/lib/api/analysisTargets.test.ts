import { afterEach, describe, expect, it, vi } from 'vitest'

import {
  askTargetQuestion,
  clearTargetQuestions,
  copyAnalysisTarget,
  createAnalysisTarget,
  deleteAnalysisTarget,
  exportTargetAnalysisMarkdown,
  exportTargetReviewsCsv,
  getAnalysisTarget,
  getIngestionRun,
  getTargetSummary,
  listAnalysisTargets,
  listTargetQuestions,
  listTargetReviews,
  renameAnalysisTarget,
  startFileImport,
  startUrlIngestion,
} from '@/lib/api/analysisTargets'

const getToken = async () => 'test-token'

function stubFetch(body: unknown, ok = true) {
  const fetchMock = vi.fn().mockResolvedValue({
    ok,
    status: ok ? 200 : 500,
    headers: new Headers(),
    json: async () => body,
  })
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}

function requestOf(fetchMock: ReturnType<typeof stubFetch>) {
  const [url, init] = fetchMock.mock.calls[0]
  return { url: url as string, init: init as RequestInit }
}

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('analysisTargets API client', () => {
  it('lists analysis targets owned by the caller', async () => {
    const fetchMock = stubFetch({ items: [{ id: 'target-1' }] })

    const items = await listAnalysisTargets(getToken)

    expect(items).toEqual([{ id: 'target-1' }])
    expect(requestOf(fetchMock).url).toContain('/api/v1/analysis-targets')
  })

  it('fetches a single analysis target by id', async () => {
    const fetchMock = stubFetch({ id: 'target-1' })

    await getAnalysisTarget('target-1', getToken)

    expect(requestOf(fetchMock).url).toContain('/analysis-targets/target-1')
  })

  it('creates an analysis target with the submitted name and source url', async () => {
    const fetchMock = stubFetch({ id: 'target-1' })

    await createAnalysisTarget({ name: 'Blue Bottle', source_url: 'https://example.com' }, getToken)

    const { init } = requestOf(fetchMock)
    expect(init.method).toBe('POST')
    expect(JSON.parse(init.body as string)).toEqual({
      name: 'Blue Bottle',
      source_url: 'https://example.com',
    })
  })

  it('renames an analysis target', async () => {
    const fetchMock = stubFetch({ id: 'target-1', name: 'New Name' })

    await renameAnalysisTarget('target-1', 'New Name', getToken)

    const { url, init } = requestOf(fetchMock)
    expect(url).toContain('/analysis-targets/target-1')
    expect(init.method).toBe('PATCH')
    expect(JSON.parse(init.body as string)).toEqual({ name: 'New Name' })
  })

  it('creates a Save As copy through the copies endpoint', async () => {
    const fetchMock = stubFetch({ id: 'target-2', name: 'Copy' })

    await copyAnalysisTarget('target-1', 'Copy', getToken)

    const { url, init } = requestOf(fetchMock)
    expect(url).toContain('/analysis-targets/target-1/copies')
    expect(init.method).toBe('POST')
    expect(JSON.parse(init.body as string)).toEqual({ name: 'Copy' })
  })

  it('deletes an analysis target', async () => {
    const fetchMock = stubFetch(null)

    await deleteAnalysisTarget('target-1', getToken)

    const { url, init } = requestOf(fetchMock)
    expect(url).toContain('/analysis-targets/target-1')
    expect(init.method).toBe('DELETE')
  })

  it('fetches the target summary', async () => {
    const fetchMock = stubFetch({ reviews_collected: 3 })

    await getTargetSummary('target-1', getToken)

    expect(requestOf(fetchMock).url).toContain('/analysis-targets/target-1/summary')
  })

  it('lists reviews with pagination only when no filters are set', async () => {
    const fetchMock = stubFetch({ items: [], total: 0, limit: 25, offset: 0 })

    await listTargetReviews('target-1', { limit: 25, offset: 0 }, getToken)

    const { url } = requestOf(fetchMock)
    expect(url).toContain('limit=25')
    expect(url).toContain('offset=0')
    expect(url).not.toContain('min_rating')
    expect(url).not.toContain('max_rating')
    expect(url).not.toContain('reviewed_after')
    expect(url).not.toContain('reviewed_before')
  })

  it('lists reviews with rating and date filters applied', async () => {
    const fetchMock = stubFetch({ items: [], total: 0, limit: 200, offset: 0 })

    await listTargetReviews(
      'target-1',
      {
        limit: 200,
        offset: 0,
        filters: {
          minRating: 1,
          maxRating: 2,
          reviewedAfter: '2026-01-01T00:00:00Z',
          reviewedBefore: '2026-02-01T23:59:59Z',
        },
      },
      getToken,
    )

    const { url } = requestOf(fetchMock)
    expect(url).toContain('min_rating=1')
    expect(url).toContain('max_rating=2')
    expect(url).toContain('reviewed_after=2026-01-01T00%3A00%3A00Z')
    expect(url).toContain('reviewed_before=2026-02-01T23%3A59%3A59Z')
  })

  it('starts URL ingestion', async () => {
    const fetchMock = stubFetch({ id: 'run-1' })

    await startUrlIngestion('target-1', getToken)

    const { url, init } = requestOf(fetchMock)
    expect(url).toContain('/analysis-targets/target-1/ingestions')
    expect(init.method).toBe('POST')
  })

  it('starts a file import with the file attached', async () => {
    const fetchMock = stubFetch({ id: 'run-1' })
    const file = new File(['review_text,rating\nGood,5\n'], 'reviews.csv', { type: 'text/csv' })

    await startFileImport('target-1', file, getToken)

    const { url, init } = requestOf(fetchMock)
    expect(url).toContain('/analysis-targets/target-1/ingestions/imports')
    expect(init.body).toBeInstanceOf(FormData)
    expect((init.body as FormData).get('file')).toBe(file)
  })

  it('fetches an ingestion run by id', async () => {
    const fetchMock = stubFetch({ id: 'run-1', status: 'succeeded' })

    await getIngestionRun('run-1', getToken)

    expect(requestOf(fetchMock).url).toContain('/ingestion-runs/run-1')
  })

  it('lists persisted questions for a target', async () => {
    const fetchMock = stubFetch({ items: [] })

    await listTargetQuestions('target-1', getToken)

    expect(requestOf(fetchMock).url).toContain('/analysis-targets/target-1/questions')
  })

  it('asks a question and posts the question text', async () => {
    const fetchMock = stubFetch({ id: 'qa-1' })

    await askTargetQuestion('target-1', 'What do customers like?', getToken)

    const { init } = requestOf(fetchMock)
    expect(init.method).toBe('POST')
    expect(JSON.parse(init.body as string)).toEqual({ question: 'What do customers like?' })
  })

  it('clears question history for a target', async () => {
    const fetchMock = stubFetch(null)

    await clearTargetQuestions('target-1', getToken)

    const { url, init } = requestOf(fetchMock)
    expect(url).toContain('/analysis-targets/target-1/questions')
    expect(init.method).toBe('DELETE')
  })

  it('requests the CSV export endpoint', async () => {
    const fetchMock = stubFetch(null)

    await exportTargetReviewsCsv('target-1', getToken)

    expect(requestOf(fetchMock).url).toContain('/analysis-targets/target-1/exports/reviews.csv')
  })

  it('requests the Markdown export endpoint', async () => {
    const fetchMock = stubFetch(null)

    await exportTargetAnalysisMarkdown('target-1', getToken)

    expect(requestOf(fetchMock).url).toContain('/analysis-targets/target-1/exports/analysis.md')
  })
})
