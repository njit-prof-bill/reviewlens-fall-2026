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
import { useRenameAnalysisTarget } from '@/hooks/useAnalysis'
import type { AnalysisTarget } from '@/lib/api/types'

interface RenameAnalysisDialogProps {
  target: AnalysisTarget | null
  onClose: () => void
}

function RenameForm({ target, onClose }: { target: AnalysisTarget; onClose: () => void }) {
  const rename = useRenameAnalysisTarget()
  const [name, setName] = useState(target.name)

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault()
    if (!name.trim()) return
    await rename.mutateAsync({ id: target.id, name: name.trim() })
    onClose()
  }

  return (
    <form onSubmit={handleSubmit}>
      <DialogHeader>
        <DialogTitle>Rename analysis</DialogTitle>
        <DialogDescription>
          Give this analysis a short name you will recognise later.
        </DialogDescription>
      </DialogHeader>

      <div className="grid gap-2 py-4">
        <Label htmlFor="analysis-name">Name</Label>
        <Input
          id="analysis-name"
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
        <Button type="submit" disabled={!name.trim() || rename.isPending}>
          {rename.isPending ? 'Saving...' : 'Save'}
        </Button>
      </DialogFooter>
    </form>
  )
}

export function RenameAnalysisDialog({ target, onClose }: RenameAnalysisDialogProps) {
  return (
    <Dialog open={target !== null} onOpenChange={(open) => !open && onClose()}>
      <DialogContent>
        {/* Keyed so the field resets when a different analysis is selected. */}
        {target ? <RenameForm key={target.id} target={target} onClose={onClose} /> : null}
      </DialogContent>
    </Dialog>
  )
}
