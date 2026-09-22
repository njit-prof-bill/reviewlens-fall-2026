import { Star } from 'lucide-react'
import { useState } from 'react'

import { formatReviewDate } from '@/components/analysis/format'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { useTargetReviews } from '@/hooks/useAnalysis'
import type { ReviewFilters } from '@/lib/api/types'

// Matches the backend's maximum page size, so browsing needs no pagination controls.
const PAGE_SIZE = 200

function toStartOfDay(value: string) {
  return value ? `${value}T00:00:00Z` : undefined
}

function toEndOfDay(value: string) {
  return value ? `${value}T23:59:59Z` : undefined
}

interface AppliedFilters {
  minRating: string
  maxRating: string
  after: string
  before: string
}

const EMPTY_FILTERS: AppliedFilters = { minRating: '', maxRating: '', after: '', before: '' }

interface ReviewDatasetDialogProps {
  targetId: string
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function ReviewDatasetDialog({
  targetId,
  open,
  onOpenChange,
}: ReviewDatasetDialogProps) {
  const [appliedFilters, setAppliedFilters] = useState<AppliedFilters>(EMPTY_FILTERS)

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      {/* Base dialog defaults to sm:max-w-sm; override it explicitly or it wins over max-w-5xl. */}
      <DialogContent className="max-w-5xl sm:max-w-5xl">
        <DialogHeader>
          <DialogTitle>Review dataset</DialogTitle>
          <DialogDescription>
            Browse the current persisted reviews for this analysis.
          </DialogDescription>
        </DialogHeader>

        {/* Remounting on open gives each session fresh pending edits without an effect. */}
        {open ? (
          <ReviewDatasetPanel
            key={targetId}
            targetId={targetId}
            applied={appliedFilters}
            onApply={(next) => {
              setAppliedFilters(next)
              onOpenChange(false)
            }}
            onCancel={() => onOpenChange(false)}
          />
        ) : null}
      </DialogContent>
    </Dialog>
  )
}

interface ReviewDatasetPanelProps {
  targetId: string
  applied: AppliedFilters
  onApply: (next: AppliedFilters) => void
  onCancel: () => void
}

function ReviewDatasetPanel({ targetId, applied, onApply, onCancel }: ReviewDatasetPanelProps) {
  const [minRating, setMinRating] = useState(applied.minRating)
  const [maxRating, setMaxRating] = useState(applied.maxRating)
  const [after, setAfter] = useState(applied.after)
  const [before, setBefore] = useState(applied.before)

  const filters: ReviewFilters = {
    minRating: applied.minRating ? Number(applied.minRating) : undefined,
    maxRating: applied.maxRating ? Number(applied.maxRating) : undefined,
    reviewedAfter: toStartOfDay(applied.after),
    reviewedBefore: toEndOfDay(applied.before),
  }
  const reviews = useTargetReviews(targetId, PAGE_SIZE, 0, filters)

  function handleApply(event: React.FormEvent) {
    event.preventDefault()
    onApply({ minRating, maxRating, after, before })
  }

  return (
    <>
      <form
        id="review-dataset-filters"
        onSubmit={handleApply}
        className="grid gap-4 sm:grid-cols-4 sm:gap-x-6"
      >
        <div className="grid gap-2">
          <Label htmlFor="min-rating">At least</Label>
          <select
            id="min-rating"
            value={minRating}
            onChange={(event) => setMinRating(event.target.value)}
            className="h-10 rounded-md border border-input bg-background px-3 text-sm"
          >
            <option value="">Any rating</option>
            <option value="1">1 star</option>
            <option value="2">2 stars</option>
            <option value="3">3 stars</option>
            <option value="4">4 stars</option>
            <option value="5">5 stars</option>
          </select>
        </div>
        <div className="grid gap-2">
          <Label htmlFor="max-rating">At most</Label>
          <select
            id="max-rating"
            value={maxRating}
            onChange={(event) => setMaxRating(event.target.value)}
            className="h-10 rounded-md border border-input bg-background px-3 text-sm"
          >
            <option value="">Any rating</option>
            <option value="1">1 star</option>
            <option value="2">2 stars</option>
            <option value="3">3 stars</option>
            <option value="4">4 stars</option>
            <option value="5">5 stars</option>
          </select>
        </div>
        <div className="grid gap-2">
          <Label htmlFor="reviewed-after">From</Label>
          <Input
            id="reviewed-after"
            type="date"
            value={after}
            onChange={(event) => setAfter(event.target.value)}
          />
        </div>
        <div className="grid gap-2">
          <Label htmlFor="reviewed-before">To</Label>
          <Input
            id="reviewed-before"
            type="date"
            value={before}
            onChange={(event) => setBefore(event.target.value)}
          />
        </div>
      </form>

      {reviews.isPending ? (
        <div className="space-y-3 py-4" aria-label="Loading reviews">
          <Skeleton className="h-8 w-full" />
          <Skeleton className="h-8 w-full" />
          <Skeleton className="h-8 w-full" />
        </div>
      ) : null}

      {reviews.data ? (
        <div className="space-y-3 overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-20">Rating</TableHead>
                <TableHead className="w-32">Date</TableHead>
                <TableHead className="w-40">Reviewer</TableHead>
                <TableHead>Review</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {reviews.data.items.map((review) => (
                <TableRow key={review.id}>
                  <TableCell className="whitespace-nowrap font-medium tabular-nums">
                    <span className="inline-flex items-center gap-1">
                      <Star className="size-3.5 fill-current text-amber-500" />
                      {review.rating.toFixed(1)}
                    </span>
                  </TableCell>
                  <TableCell className="whitespace-nowrap text-muted-foreground">
                    {formatReviewDate(review.reviewed_at)}
                  </TableCell>
                  <TableCell className="truncate">
                    {review.reviewer_name ?? 'Anonymous'}
                  </TableCell>
                  <TableCell className="min-w-96 text-muted-foreground">
                    {review.review_text}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          <div className="flex items-center justify-between">
            <p className="text-xs text-muted-foreground">
              Showing {reviews.data.items.length} of {reviews.data.total} reviews
            </p>
          </div>
        </div>
      ) : null}

      <DialogFooter>
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" form="review-dataset-filters">
          OK
        </Button>
      </DialogFooter>
    </>
  )
}