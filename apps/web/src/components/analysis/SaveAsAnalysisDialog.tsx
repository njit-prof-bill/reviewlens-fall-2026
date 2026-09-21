import { useState } from 'react'

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
import { useCopyAnalysisTarget } from '@/hooks/useAnalysis'
import type { AnalysisTarget } from '@/lib/api/types'

interface SaveAsAnalysisDialogProps {
  target: AnalysisTarget | null
  onClose: () => void
  onCopied: (target: AnalysisTarget) => void
}

function SaveAsForm({
  target,
  onClose,
  onCopied,
}: {
  target: AnalysisTarget
  onClose: () => void
  onCopied: (target: AnalysisTarget) => void
}) {
  const copy = useCopyAnalysisTarget()
  const [name, setName] = useState(`${target.name} Copy`)

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault()
    const trimmed = name.trim()
    if (!trimmed) return
    const copied = await copy.mutateAsync({ id: target.id, name: trimmed })
    onClose()
    onCopied(copied)
  }

  return (
    <form onSubmit={handleSubmit}>
      <DialogHeader>
        <DialogTitle>Save as new analysis</DialogTitle>
        <DialogDescription>
          Create a separate analysis with the current review dataset. Q&A history starts empty.
        </DialogDescription>
      </DialogHeader>

      <div className="grid gap-2 py-4">
        <Label htmlFor="copy-analysis-name">Name</Label>
        <Input
          id="copy-analysis-name"
          value={name}
          onChange={(event) => setName(event.target.value)}
          maxLength={200}
          autoFocus
        />
      </div>

      <DialogFooter>
        <Button type="button" variant="outline" onClick={onClose}>
          Cancel
        </Button>
        <Button type="submit" disabled={!name.trim() || copy.isPending}>
          {copy.isPending ? 'Saving...' : 'Save As'}
        </Button>
      </DialogFooter>
    </form>
  )
}

export function SaveAsAnalysisDialog({
  target,
  onClose,
  onCopied,
}: SaveAsAnalysisDialogProps) {
  return (
    <Dialog open={target !== null} onOpenChange={(open) => !open && onClose()}>
      <DialogContent>
        {target ? (
          <SaveAsForm
            key={target.id}
            target={target}
            onClose={onClose}
            onCopied={onCopied}
          />
        ) : null}
      </DialogContent>
    </Dialog>
  )
}