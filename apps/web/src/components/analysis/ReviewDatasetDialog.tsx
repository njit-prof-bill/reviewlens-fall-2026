import { Star } from 'lucide-react'
import { useState } from 'react'

import { formatReviewDate } from '@/components/analysis/format'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
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

const PAGE_SIZE = 25

function toStartOfDay(value: string) {
  return value ? `${value}T00:00:00Z` : undefined
}

function toEndOfDay(value: string) {
  return value ? `${value}T23:59:59Z` : undefined
}

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
  const [offset, setOffset] = useState(0)
  const [minRating, setMinRating] = useState('')
  const [maxRating, setMaxRating] = useState('')
  const [after, setAfter] = useState('')
  const [before, setBefore] = useState('')

  const filters: ReviewFilters = {
    minRating: minRating ? Number(minRating) : undefined,
    maxRating: maxRating ? Number(maxRating) : undefined,
    reviewedAfter: toStartOfDay(after),
    reviewedBefore: toEndOfDay(before),
  }
  const reviews = useTargetReviews(targetId, PAGE_SIZE, offset, filters)
  const canGoBack = offset > 0
  const canGoForward = Boolean(reviews.data && offset + PAGE_SIZE < reviews.data.total)

  function resetAnd(setter: (value: string) => void, value: string) {
    setter(value)
    setOffset(0)
  }

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

        <div className="grid gap-4 sm:grid-cols-4 sm:gap-x-6">
          <div className="grid gap-2">
            <Label htmlFor="min-rating">At least</Label>
            <select
              id="min-rating"
              value={minRating}
              onChange={(event) => resetAnd(setMinRating, event.target.value)}
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
              onChange={(event) => resetAnd(setMaxRating, event.target.value)}
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
              onChange={(event) => resetAnd(setAfter, event.target.value)}
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="reviewed-before">To</Label>
            <Input
              id="reviewed-before"
              type="date"
              value={before}
              onChange={(event) => resetAnd(setBefore, event.target.value)}
            />
          </div>
        </div>

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
              <div className="flex gap-2">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  disabled={!canGoBack}
                  onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}
                >
                  Previous
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  disabled={!canGoForward}
                  onClick={() => setOffset(offset + PAGE_SIZE)}
                >
                  Next
                </Button>
              </div>
            </div>
          </div>
        ) : null}
      </DialogContent>
    </Dialog>
  )
}