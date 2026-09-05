import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { useDeleteAnalysisTarget } from '@/hooks/useAnalysis'
import type { AnalysisTarget } from '@/lib/api/types'

interface DeleteAnalysisDialogProps {
  target: AnalysisTarget | null
  onClose: () => void
  onDeleted?: (id: string) => void
}

export function DeleteAnalysisDialog({
  target,
  onClose,
  onDeleted,
}: DeleteAnalysisDialogProps) {
  const deleteTarget = useDeleteAnalysisTarget()

  async function confirmDelete() {
    if (!target) return
    const deletedId = target.id
    await deleteTarget.mutateAsync(deletedId)
    onClose()
    onDeleted?.(deletedId)
  }

  return (
    <AlertDialog open={target !== null} onOpenChange={(open) => !open && onClose()}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Delete this analysis?</AlertDialogTitle>
          <AlertDialogDescription>
            {target?.name} and every review collected for it will be permanently removed.
            This cannot be undone.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <AlertDialogAction
            onClick={(event) => {
              // Deletion is awaited, so the dialog must not self-close first.
              event.preventDefault()
              void confirmDelete()
            }}
            disabled={deleteTarget.isPending}
          >
            {deleteTarget.isPending ? 'Deleting...' : 'Delete'}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}
