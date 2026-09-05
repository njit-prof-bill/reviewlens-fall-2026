import { cn } from '@/lib/utils'

interface NotebookStepProps {
  step: number
  title: string
  action?: React.ReactNode
  children: React.ReactNode
  className?: string
}

/** Numbered vertical progression from the reference wireframe. */
export function NotebookStep({ step, title, action, children, className }: NotebookStepProps) {
  return (
    <section className={cn('flex gap-4', className)}>
      <div className="flex flex-col items-center">
        <span
          aria-hidden="true"
          className="flex size-7 shrink-0 items-center justify-center rounded-full border border-border bg-background text-xs font-semibold text-muted-foreground"
        >
          {step}
        </span>
        <span className="mt-2 w-px flex-1 bg-border" aria-hidden="true" />
      </div>

      <div className="min-w-0 flex-1 pb-8">
        <div className="mb-3 flex items-center justify-between gap-3">
          <h2 className="text-sm font-semibold text-foreground">{title}</h2>
          {action}
        </div>
        {children}
      </div>
    </section>
  )
}
