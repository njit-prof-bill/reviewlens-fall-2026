import { Download, ExternalLink, FileText, FileUp, RefreshCw } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useParams, useSearchParams } from 'react-router-dom'
import { useQueryClient } from '@tanstack/react-query'

import { CurrentAnalysisScopePanel } from '@/components/analysis/CurrentAnalysisScopePanel'
import { ImportReviewsDialog } from '@/components/analysis/ImportReviewsDialog'
import { IngestionSummaryCard } from '@/components/analysis/IngestionSummaryCard'
import { NotebookStep } from '@/components/analysis/NotebookStep'
import {
  ReviewDatasetDialog,
} from '@/components/analysis/ReviewDatasetDialog'
import { ReviewPreviewTable } from '@/components/analysis/ReviewPreviewTable'
import { ReviewQANotebook } from '@/components/analysis/ReviewQANotebook'
import {
  EMPTY_FILTERS,
  hasActiveFilters,
  toReviewFilters,
  type AppliedFilters,
} from '@/components/analysis/reviewFilters'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import {
  analysisKeys,
  useAnalysisTarget,
  useIngestionRun,
  useStartIngestion,
  useTargetReviews,
  useTargetSummary,
} from '@/hooks/useAnalysis'
import { exportTargetAnalysisMarkdown, exportTargetReviewsCsv } from '@/lib/api/analysisTargets'
import { ApiError } from '@/lib/api/client'
import { isTerminal, platformLabel } from '@/lib/api/types'
import { useApiToken } from '@/hooks/useApiToken'

const PREVIEW_SIZE = 5

export function AnalysisWorkspace() {
  const { targetId } = useParams<{ targetId: string }>()
  const [searchParams] = useSearchParams()
  const queryClient = useQueryClient()
  const getToken = useApiToken()
  const [activeRunId, setActiveRunId] = useState<string | undefined>(
    searchParams.get('run') ?? undefined,
  )
  const [isImportOpen, setImportOpen] = useState(false)
  const [isDatasetOpen, setDatasetOpen] = useState(false)
  const [isExporting, setExporting] = useState(false)
  const [appliedFilters, setAppliedFilters] = useState<AppliedFilters>(EMPTY_FILTERS)
  const [previewSize] = useState(PREVIEW_SIZE)

  const target = useAnalysisTarget(targetId)
  const summary = useTargetSummary(targetId)
  const reviews = useTargetReviews(targetId, previewSize, 0, toReviewFilters(appliedFilters))
  const run = useIngestionRun(activeRunId)
  const startIngestion = useStartIngestion(targetId)

  const runStatus = run.data?.status
  const isRunning = Boolean(activeRunId) && !isTerminal(runStatus)

  // Once a run settles, pull the derived views back into sync.
  useEffect(() => {
    if (!targetId || !isTerminal(runStatus)) return
    queryClient.invalidateQueries({ queryKey: analysisKeys.all })
    queryClient.invalidateQueries({ queryKey: analysisKeys.detail(targetId) })
    queryClient.invalidateQueries({ queryKey: analysisKeys.summary(targetId) })
    queryClient.invalidateQueries({ queryKey: ['analysis-targets', targetId, 'reviews'] })
  }, [targetId, runStatus, queryClient])

  async function beginIngestion(file?: File) {
    const started = await startIngestion.mutateAsync(file)
    setActiveRunId(started.id)
    return started
  }

  async function downloadExport(kind: 'csv' | 'markdown') {
    if (!targetId || isExporting) return
    setExporting(true)
    try {
      const response =
        kind === 'csv'
          ? await exportTargetReviewsCsv(targetId, getToken)
          : await exportTargetAnalysisMarkdown(targetId, getToken)
      const blob = await response.blob()
      const disposition = response.headers.get('content-disposition') ?? ''
      const filename = disposition.match(/filename="([^"]+)"/)?.[1] ??
        (kind === 'csv' ? 'reviews.csv' : 'analysis.md')
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      link.click()
      URL.revokeObjectURL(url)
    } finally {
      setExporting(false)
    }
  }

  if (target.isPending) {
    return (
      <div className="mx-auto max-w-5xl space-y-4 px-4 py-8">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-32 w-full" />
      </div>
    )
  }

  if (target.isError) {
    const notFound = target.error instanceof ApiError && target.error.isNotFound
    return (
      <div className="mx-auto max-w-xl px-4 py-24 text-center">
        <h1 className="text-lg font-semibold text-foreground">
          {notFound ? 'Analysis not available' : 'Something went wrong'}
        </h1>
        <p className="mt-2 text-sm text-muted-foreground">
          {notFound
            ? 'This analysis does not exist, or it belongs to another account.'
            : 'The analysis could not be loaded. Please try again.'}
        </p>
      </div>
    )
  }

  const showFallbackProminently = summary.data?.latest_run?.status === 'failed'
  const latestStatus = summary.data?.latest_run?.status
  const qaEnabled =
    Boolean(summary.data?.reviews_collected) &&
    latestStatus !== 'pending' &&
    latestStatus !== 'processing' &&
    latestStatus !== 'failed'

  return (
    <div className="mx-auto grid max-w-6xl grid-cols-1 gap-8 px-4 py-8 lg:grid-cols-[minmax(0,1fr)_18rem]">
      <div className="min-w-0">
        <header className="mb-8">
          <h1 className="truncate text-xl font-semibold tracking-tight text-foreground">
            {target.data.name}
          </h1>
          <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-muted-foreground">
            <span>{platformLabel(target.data.platform)}</span>
            <a
              href={target.data.source_url}
              target="_blank"
              rel="noreferrer"
              className="inline-flex max-w-md items-center gap-1 truncate underline underline-offset-4 hover:text-foreground"
            >
              <span className="truncate">{target.data.source_url}</span>
              <ExternalLink className="size-3 shrink-0" aria-hidden="true" />
            </a>
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            <Button
              type="button"
              variant="outline"
              size="sm"
              disabled={isExporting || !summary.data?.reviews_collected}
              onClick={() => void downloadExport('csv')}
            >
              <Download className="size-4" />
              Export CSV
            </Button>
            <Button
              type="button"
              variant="outline"
              size="sm"
              disabled={isExporting}
              onClick={() => void downloadExport('markdown')}
            >
              <FileText className="size-4" />
              Export Markdown
            </Button>
          </div>
        </header>

        <NotebookStep
          step={1}
          title="Ingestion Summary"
          action={
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => void beginIngestion()}
                disabled={isRunning || startIngestion.isPending}
              >
                <RefreshCw className={isRunning ? 'size-4 animate-spin' : 'size-4'} />
                {isRunning ? 'Refreshing...' : 'Refresh Reviews'}
              </Button>
              <Button
                variant={showFallbackProminently ? 'secondary' : 'ghost'}
                size="sm"
                onClick={() => setImportOpen(true)}
                disabled={isRunning}
              >
                <FileUp className="size-4" />
                Import reviews instead
              </Button>
            </div>
          }
        >
          <IngestionSummaryCard
            summary={summary.data}
            isLoading={summary.isPending || isRunning}
            onRatingFilter={(rating) =>
              setAppliedFilters({
                minRating: String(rating),
                maxRating: String(rating),
                after: '',
                before: '',
              })
            }
          />
        </NotebookStep>

        <NotebookStep step={2} title="Review Preview">
          {hasActiveFilters(appliedFilters) ? (
            <div className="mb-3 flex items-center justify-between gap-2 rounded-md border border-border bg-muted/40 px-3 py-2 text-xs text-muted-foreground">
              <span>Filtered to matching reviews only.</span>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="h-auto px-2 py-1"
                onClick={() => setAppliedFilters(EMPTY_FILTERS)}
              >
                Clear filters
              </Button>
            </div>
          ) : null}
          <ReviewPreviewTable
            reviews={reviews.data}
            isLoading={reviews.isPending || isRunning}
            canViewMore={Boolean(
              reviews.data && reviews.data.items.length < reviews.data.total,
            )}
            onViewMore={() => setDatasetOpen(true)}
          />
          {reviews.data?.total || hasActiveFilters(appliedFilters) ? (
            <Button
              type="button"
              variant="outline"
              className="mt-3"
              onClick={() => setDatasetOpen(true)}
            >
              Browse and filter reviews
            </Button>
          ) : null}
        </NotebookStep>

        <NotebookStep step={3} title="Ask the Reviews">
          <ReviewQANotebook
            targetId={target.data.id}
            targetName={target.data.name}
            enabled={qaEnabled}
          />
        </NotebookStep>
      </div>

      <aside>
        <CurrentAnalysisScopePanel summary={summary.data} />
      </aside>

      <ImportReviewsDialog
        open={isImportOpen}
        onOpenChange={setImportOpen}
        onImport={beginIngestion}
        isImporting={startIngestion.isPending}
      />
      {targetId ? (
        <ReviewDatasetDialog
          targetId={targetId}
          open={isDatasetOpen}
          onOpenChange={setDatasetOpen}
          applied={appliedFilters}
          onApply={setAppliedFilters}
        />
      ) : null}
    </div>
  )
}
