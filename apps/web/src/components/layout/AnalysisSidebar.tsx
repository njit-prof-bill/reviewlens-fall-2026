import { MoreHorizontal, PencilLine, Plus, Trash2 } from 'lucide-react'
import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'

import { DeleteAnalysisDialog } from '@/components/analysis/DeleteAnalysisDialog'
import { RenameAnalysisDialog } from '@/components/analysis/RenameAnalysisDialog'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Skeleton } from '@/components/ui/skeleton'
import { useAnalysisTargets } from '@/hooks/useAnalysis'
import type { AnalysisTarget } from '@/lib/api/types'
import { cn } from '@/lib/utils'

interface AnalysisSidebarProps extends React.HTMLAttributes<HTMLElement> {
  isOpen?: boolean
  onNavigate?: () => void
}

export function AnalysisSidebar({
  className,
  isOpen = false,
  onNavigate,
  ...props
}: AnalysisSidebarProps) {
  const location = useLocation()
  const navigate = useNavigate()
  const { data: targets, isPending, isError } = useAnalysisTargets()

  const [renaming, setRenaming] = useState<AnalysisTarget | null>(null)
  const [pendingDelete, setPendingDelete] = useState<AnalysisTarget | null>(null)

  function handleDeleted(deletedId: string) {
    if (location.pathname === `/analysis/${deletedId}`) {
      navigate('/')
    }
  }

  return (
    <nav
      aria-label="Analyses"
      className={cn(
        'fixed inset-y-14 left-0 z-30 flex w-64 shrink-0 flex-col overflow-y-auto border-r border-border bg-sidebar transition-transform duration-200 md:static md:inset-auto md:translate-x-0',
        isOpen ? 'translate-x-0' : '-translate-x-full',
        className,
      )}
      {...props}
    >
      <div className="p-3">
        <Button asChild className="mb-4 w-full justify-start gap-2">
          <Link to="/" onClick={onNavigate}>
            <Plus className="size-4" />
            New Analysis
          </Link>
        </Button>

        <p className="px-2 pb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
          Your analyses
        </p>

        {isPending ? (
          <div className="space-y-2 px-2" aria-label="Loading analyses">
            <Skeleton className="h-8 w-full" />
            <Skeleton className="h-8 w-full" />
            <Skeleton className="h-8 w-full" />
          </div>
        ) : null}

        {isError ? (
          <p className="px-2 text-sm text-muted-foreground">
            Your analyses could not be loaded.
          </p>
        ) : null}

        {targets && targets.length === 0 ? (
          <p className="px-2 text-sm text-muted-foreground">
            No analyses yet. Paste a Google Maps link to create your first one.
          </p>
        ) : null}

        <ul className="space-y-1">
          {targets?.map((target) => {
            const isActive = location.pathname === `/analysis/${target.id}`

            return (
              <li key={target.id} className="group/item relative">
                <Button
                  asChild
                  variant="ghost"
                  className={cn(
                    'h-9 w-full justify-start rounded-md px-2.5 pr-9 text-sm font-normal text-muted-foreground',
                    isActive && 'bg-accent text-foreground hover:bg-accent',
                  )}
                >
                  <Link
                    to={`/analysis/${target.id}`}
                    onClick={onNavigate}
                    aria-current={isActive ? 'page' : undefined}
                  >
                    <span className="truncate">{target.name}</span>
                  </Link>
                </Button>

                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="absolute right-1 top-1 size-7 opacity-0 focus-visible:opacity-100 group-hover/item:opacity-100"
                      aria-label={`Actions for ${target.name}`}
                    >
                      <MoreHorizontal className="size-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="w-40">
                    <DropdownMenuItem
                      onSelect={(event) => {
                        // Let the menu finish closing before the dialog takes focus.
                        event.preventDefault()
                        setRenaming(target)
                      }}
                    >
                      <PencilLine className="size-4" />
                      Rename
                    </DropdownMenuItem>
                    <DropdownMenuItem
                      className="text-destructive focus:text-destructive"
                      onSelect={(event) => {
                        event.preventDefault()
                        setPendingDelete(target)
                      }}
                    >
                      <Trash2 className="size-4" />
                      Delete
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </li>
            )
          })}
        </ul>
      </div>

      <RenameAnalysisDialog target={renaming} onClose={() => setRenaming(null)} />

      <DeleteAnalysisDialog
        target={pendingDelete}
        onClose={() => setPendingDelete(null)}
        onDeleted={handleDeleted}
      />
    </nav>
  )
}
