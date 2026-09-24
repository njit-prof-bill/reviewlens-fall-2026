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

function ChartHeading({ title, detail }: { title: string; detail: string }) {
  return (
    <div className="flex items-baseline justify-between gap-3">
      <h3 className="text-sm font-medium text-foreground">{title}</h3>
      <span className="text-xs text-muted-foreground">{detail}</span>
    </div>
  )
}

function formatMonth(period: string): string {
  const [year, month] = period.split('-').map(Number)
  if (!year || !month) return period
  return `${new Intl.DateTimeFormat('en', { month: 'short' }).format(
    new Date(Date.UTC(year, month - 1, 1)),
  )} '${String(year).slice(-2)}`
}

function shouldShowMonthLabel(index: number, count: number): boolean {
  if (count <= 6) return true
  const interval = (count - 1) / 5
  return (
    index === 0 ||
    index === count - 1 ||
    Math.abs(index / interval - Math.round(index / interval)) < 0.01
  )
}

function RatingDistribution({
  distribution,
  onRatingFilter,
}: {
  distribution: Array<{ rating: number; count: number }>
  onRatingFilter?: (rating: number) => void
}) {
  const maximum = Math.max(...distribution.map((point) => point.count), 1)
  return (
    <div className="space-y-3">
      <ChartHeading title="Rating distribution" detail="reviews by star rating" />
      <div className="grid grid-cols-5 items-end gap-2" aria-label="Rating distribution chart">
        {distribution.map((point) => (
          <button
            key={point.rating}
            type="button"
            className="group flex min-w-0 flex-col items-center gap-1"
            onClick={() => onRatingFilter?.(point.rating)}
            aria-label={`Filter to ${point.rating} star reviews: ${point.count} reviews`}
            disabled={!onRatingFilter}
          >
            <span className="text-xs tabular-nums text-muted-foreground">{point.count}</span>
            <span
              className="w-full rounded-t-sm bg-primary/75 transition-colors group-hover:bg-primary"
              style={{ height: `${Math.max((point.count / maximum) * 72, point.count ? 8 : 2)}px` }}
            />
            <span className="text-xs tabular-nums text-muted-foreground">{point.rating} star</span>
          </button>
        ))}
      </div>
    </div>
  )
}

function MonthlyVolumeChart({ volume }: { volume: Array<{ period: string; count: number }> }) {
  if (volume.length === 0) {
    return <p className="text-sm text-muted-foreground">No dated reviews are available.</p>
  }
  const visible = volume.slice(-12)
  const maximum = Math.max(...visible.map((point) => point.count), 1)
  return (
    <div className="space-y-3">
      <ChartHeading title="Review volume" detail="monthly, latest 12 months" />
      <div
        className="grid min-h-28 grid-flow-col auto-cols-fr items-end gap-1.5"
        role="img"
        aria-label="Monthly review volume chart"
      >
        {visible.map((point, index) => (
          <div key={point.period} className="flex min-w-0 flex-col items-center gap-1">
            <span className="text-[10px] tabular-nums text-muted-foreground">{point.count}</span>
            <span
              className="w-full rounded-t-sm bg-emerald-500/70"
              style={{ height: `${Math.max((point.count / maximum) * 64, 4)}px` }}
            />
            <span className="h-3 truncate text-[10px] text-muted-foreground">
              {shouldShowMonthLabel(index, visible.length) ? formatMonth(point.period) : ''}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

function AverageRatingChart({
  averages,
}: {
  averages: Array<{ period: string; average_rating: number }>
}) {
  if (averages.length === 0) {
    return <p className="text-sm text-muted-foreground">No dated reviews are available.</p>
  }
  const visible = averages.slice(-12)
  const chartWidth = 240
  const chartTop = 8
  const chartBottom = 60
  const xStep = visible.length > 1 ? chartWidth / (visible.length - 1) : 0
  const points = visible
    .map((point, index) => {
      const x = visible.length > 1 ? index * xStep : chartWidth / 2
      const y = chartBottom - (point.average_rating / 5) * (chartBottom - chartTop)
      return `${x},${y}`
    })
    .join(' ')
  return (
    <div className="space-y-3">
      <ChartHeading title="Average rating over time" detail="monthly average, latest 12 months" />
      <div role="img" aria-label="Average rating over time chart">
        <svg
          viewBox={`0 0 ${chartWidth} 76`}
          className="h-20 w-full overflow-visible"
          aria-hidden="true"
        >
          <line x1="0" y1={chartTop} x2={chartWidth} y2={chartTop} stroke="currentColor" strokeOpacity="0.12" />
          <line x1="0" y1={chartBottom} x2={chartWidth} y2={chartBottom} stroke="currentColor" strokeOpacity="0.2" />
          <polyline points={points} fill="none" stroke="rgb(245 158 11)" strokeWidth="2" vectorEffect="non-scaling-stroke" />
          {visible.map((point, index) => {
            const x = visible.length > 1 ? index * xStep : chartWidth / 2
            const y = chartBottom - (point.average_rating / 5) * (chartBottom - chartTop)
            return <circle key={point.period} cx={x} cy={y} r="2.5" fill="rgb(245 158 11)" />
          })}
        </svg>
        <div className="grid grid-cols-6 text-[10px] text-muted-foreground">
          {visible.map((point, index) => (
            <span key={point.period} className="truncate text-center">
              {shouldShowMonthLabel(index, visible.length) ? formatMonth(point.period) : ''}
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}

interface IngestionSummaryCardProps {
  summary: AnalysisTargetSummary | undefined
  isLoading: boolean
  onRatingFilter?: (rating: number) => void
}

const REJECTION_REASON_LABELS: Record<string, string> = {
  missing_review_text: 'missing review text',
  missing_or_invalid_rating: 'missing or invalid rating',
}

function rejectionSummary(reasons: Record<string, number> | null): string {
  if (!reasons) return 'No reason details were recorded.'
  return Object.entries(reasons)
    .map(([reason, count]) => `${count} ${REJECTION_REASON_LABELS[reason] ?? reason}`)
    .join(', ')
}

export function IngestionSummaryCard({ summary, isLoading, onRatingFilter }: IngestionSummaryCardProps) {
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
          <>
            <dl className="grid grid-cols-2 gap-6 sm:grid-cols-4">
              <Stat label="Reviews collected" value={String(summary.reviews_collected)} />
              <Stat label="Average rating" value={formatRating(summary.average_rating)} />
              <Stat label="Earliest review" value={formatReviewDate(summary.earliest_review)} />
              <Stat label="Latest review" value={formatReviewDate(summary.latest_review)} />
            </dl>
            <div className="grid gap-5 border-t border-border pt-5 lg:grid-cols-3">
              <RatingDistribution
                distribution={summary.rating_distribution}
                onRatingFilter={onRatingFilter}
              />
              <MonthlyVolumeChart volume={summary.review_volume_by_month} />
              <AverageRatingChart averages={summary.average_rating_by_month} />
            </div>
          </>
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
              {run.reviews_ingested} collected and {run.reviews_rejected} skipped:{' '}
              {rejectionSummary(run.rejection_reasons)}.
            </AlertDescription>
          </Alert>
        ) : null}
      </CardContent>
    </Card>
  )
}
