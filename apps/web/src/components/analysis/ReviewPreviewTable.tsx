import { Star } from 'lucide-react'

import { formatReviewDate } from '@/components/analysis/format'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import type { ReviewList } from '@/lib/api/types'

interface ReviewPreviewTableProps {
  reviews: ReviewList | undefined
  isLoading: boolean
  onViewMore?: () => void
  canViewMore?: boolean
}

export function ReviewPreviewTable({
  reviews,
  isLoading,
  onViewMore,
  canViewMore,
}: ReviewPreviewTableProps) {
  if (isLoading) {
    return (
      <Card>
        <CardContent className="space-y-3">
          {Array.from({ length: 3 }).map((_, index) => (
            <Skeleton key={index} className="h-8 w-full" />
          ))}
        </CardContent>
      </Card>
    )
  }

  if (!reviews || reviews.items.length === 0) {
    return (
      <Card>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Reviews will appear here once they have been collected.
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardContent className="space-y-4">
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
            {reviews.items.map((review) => (
              <TableRow key={review.id}>
                <TableCell className="whitespace-nowrap font-medium tabular-nums">
                  <span className="inline-flex items-center gap-1">
                    <Star className="size-3.5 fill-current text-amber-500" aria-hidden="true" />
                    {review.rating.toFixed(1)}
                  </span>
                </TableCell>
                <TableCell className="whitespace-nowrap text-muted-foreground">
                  {formatReviewDate(review.reviewed_at)}
                </TableCell>
                <TableCell className="truncate">{review.reviewer_name ?? 'Anonymous'}</TableCell>
                <TableCell className="text-muted-foreground">{review.review_text}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>

        <div className="flex items-center justify-between">
          <p className="text-xs text-muted-foreground">
            Showing {reviews.items.length} of {reviews.total} reviews
          </p>
          {canViewMore ? (
            <Button variant="outline" size="sm" onClick={onViewMore}>
              View more reviews
            </Button>
          ) : null}
        </div>
      </CardContent>
    </Card>
  )
}
