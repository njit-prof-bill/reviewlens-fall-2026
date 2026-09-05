import { Upload } from 'lucide-react'
import { useRef, useState } from 'react'

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
import { ApiError } from '@/lib/api/client'

const ALLOWED_EXTENSIONS = ['.csv', '.json']
const MAX_BYTES = 2 * 1024 * 1024

interface ImportReviewsDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onImport: (file: File) => Promise<unknown>
  isImporting: boolean
}

export function ImportReviewsDialog({
  open,
  onOpenChange,
  onImport,
  isImporting,
}: ImportReviewsDialogProps) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault()
    setError(null)

    const file = inputRef.current?.files?.[0]
    if (!file) {
      setError('Choose a .csv or .json file to import.')
      return
    }

    const name = file.name.toLowerCase()
    if (!ALLOWED_EXTENSIONS.some((extension) => name.endsWith(extension))) {
      setError('Upload a .csv or .json file.')
      return
    }

    if (file.size > MAX_BYTES) {
      setError('The file must be 2 MB or smaller.')
      return
    }

    try {
      await onImport(file)
      onOpenChange(false)
    } catch (caught) {
      setError(
        caught instanceof ApiError
          ? caught.displayMessage
          : 'The reviews could not be imported. Please try again.',
      )
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Import reviews from a file</DialogTitle>
            <DialogDescription>
              Use this when the live review source is unavailable. Supported formats are
              .csv and .json containing review text and a rating.
            </DialogDescription>
          </DialogHeader>

          <div className="grid gap-2 py-4">
            <Label htmlFor="review-file">Review file</Label>
            <Input
              id="review-file"
              ref={inputRef}
              type="file"
              accept=".csv,.json"
              onChange={() => setError(null)}
            />
            {error ? (
              <p role="alert" className="text-sm text-destructive">
                {error}
              </p>
            ) : null}
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={isImporting}>
              <Upload className="size-4" />
              {isImporting ? 'Importing...' : 'Import reviews'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
