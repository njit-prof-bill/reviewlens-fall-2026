import { AlertTriangle, CheckCircle2, CircleDashed, Loader2 } from 'lucide-react'

import {
  DISPLAY_STATE_LABELS,
  formatRating,
  formatReviewDate,
  toDisplayState,
  type DisplayState,
} from '@/components/analysis/format'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { platformLabel, type AnalysisTargetSummary } from '@/lib/api/types'

const STATE_ICONS: Record<DisplayState, React.ComponentType<{ className?: string }>> = {
  'not-started': CircleDashed,
  processing: Loader2,
  complete: CheckCircle2,
  partial: AlertTriangle,
  failed: AlertTriangle,
}

function StatusBadge({ state }: { state: DisplayState }) {
  const Icon = STATE_ICONS[state]
  const variant =
    state === 'failed' ? 'destructive' : state === 'complete' ? 'default' : 'secondary'

  return (
    <Badge variant={variant} className="gap-1.5">
      <Icon className={state === 'processing' ? 'size-3 animate-spin' : 'size-3'} />
      {DISPLAY_STATE_LABELS[state]}
    </Badge>
  )
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs uppercase tracking-wide text-muted-foreground">{label}</dt>
      <dd className="mt-1 text-lg font-semibold tabular-nums text-foreground">{value}</dd>
    </div>
  )
}

interface IngestionSummaryCardProps {
  summary: AnalysisTargetSummary | undefined
  isLoading: boolean
}

export function IngestionSummaryCard({ summary, isLoading }: IngestionSummaryCardProps) {
  if (isLoading || !summary) {
    return (
      <Card>
        <CardContent className="grid grid-cols-2 gap-6 sm:grid-cols-4">
          {Array.from({ length: 4 }).map((_, index) => (
            <Skeleton key={index} className="h-12 w-full" />
          ))}
        </CardContent>
      </Card>
    )
  }

  const state = toDisplayState(summary.latest_run?.status)
  const run = summary.latest_run

  return (
    <Card>
      <CardContent className="space-y-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="min-w-0">
            <p className="truncate text-sm font-medium text-foreground">
              {summary.entity_name}
            </p>
            <p className="text-xs text-muted-foreground">
              {platformLabel(summary.platform)}
            </p>
          </div>
          <StatusBadge state={state} />
        </div>

        {state === 'not-started' ? (
          <p className="text-sm text-muted-foreground">
            No reviews have been collected for this analysis yet.
          </p>
        ) : (
          <dl className="grid grid-cols-2 gap-6 sm:grid-cols-4">
            <Stat label="Reviews collected" value={String(summary.reviews_collected)} />
            <Stat label="Average rating" value={formatRating(summary.average_rating)} />
            <Stat label="Earliest review" value={formatReviewDate(summary.earliest_review)} />
            <Stat label="Latest review" value={formatReviewDate(summary.latest_review)} />
          </dl>
        )}

        {state === 'failed' && run?.error_message ? (
          <Alert variant="destructive">
            <AlertTriangle className="size-4" />
            <AlertTitle>Review collection failed</AlertTitle>
            <AlertDescription>{run.error_message}</AlertDescription>
          </Alert>
        ) : null}

        {state === 'partial' && run ? (
          <Alert>
            <AlertTriangle className="size-4" />
            <AlertTitle>Some reviews could not be used</AlertTitle>
            <AlertDescription>
              {run.reviews_ingested} collected, {run.reviews_rejected} skipped because they
              were missing review text or a rating.
            </AlertDescription>
          </Alert>
        ) : null}
      </CardContent>
    </Card>
  )
}
