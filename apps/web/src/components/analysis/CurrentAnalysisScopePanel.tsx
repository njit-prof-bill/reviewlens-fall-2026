import { formatDateRange } from '@/components/analysis/format'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { platformLabel, type AnalysisTargetSummary } from '@/lib/api/types'

function ScopeRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col gap-0.5">
      <dt className="text-xs uppercase tracking-wide text-muted-foreground">{label}</dt>
      <dd className="break-words text-sm font-medium text-foreground">{value}</dd>
    </div>
  )
}

interface CurrentAnalysisScopePanelProps {
  summary: AnalysisTargetSummary | undefined
}

export function CurrentAnalysisScopePanel({ summary }: CurrentAnalysisScopePanelProps) {
  if (!summary) return null

  return (
    <Card className="lg:sticky lg:top-6">
      <CardHeader>
        <CardTitle className="text-sm">Current Analysis Scope</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <dl className="space-y-4">
          <ScopeRow label="Business" value={summary.entity_name} />
          <ScopeRow label="Platform" value={platformLabel(summary.platform)} />
          <ScopeRow label="Reviews analyzed" value={String(summary.reviews_collected)} />
          <ScopeRow
            label="Date range"
            value={formatDateRange(summary.earliest_review, summary.latest_review)}
          />
        </dl>

        <Separator />

        <p className="text-xs leading-relaxed text-muted-foreground">
          This AI will answer questions only from this dataset.
        </p>
      </CardContent>
    </Card>
  )
}
