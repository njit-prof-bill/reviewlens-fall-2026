import { Loader2, Search } from 'lucide-react'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useCreateAnalysisTarget } from '@/hooks/useAnalysis'
import { startUrlIngestion } from '@/lib/api/analysisTargets'
import { ApiError } from '@/lib/api/client'
import { useApiToken } from '@/hooks/useApiToken'
import { deriveWorkingName, validateSourceUrl } from '@/lib/sourceUrl'

/**
 * Deliberately sparse: a URL field and one action, per the reference wireframe.
 * Analyzing creates the target and immediately begins collection so the flow is
 * a single gesture.
 */
export function NewAnalysis() {
  const navigate = useNavigate()
  const getToken = useApiToken()
  const createTarget = useCreateAnalysisTarget()
  const [url, setUrl] = useState('')
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault()

    const validationError = validateSourceUrl(url)
    if (validationError) {
      setError(validationError)
      return
    }
    setError(null)

    try {
      const target = await createTarget.mutateAsync({
        name: deriveWorkingName(url),
        source_url: url.trim(),
      })
      const run = await startUrlIngestion(target.id, getToken)
      navigate(`/analysis/${target.id}?run=${run.id}`)
    } catch (caught) {
      setError(
        caught instanceof ApiError
          ? caught.displayMessage
          : 'The analysis could not be started. Please try again.',
      )
    }
  }

  return (
    <div className="mx-auto flex max-w-2xl flex-col justify-center px-4 py-24">
      <h1 className="text-2xl font-semibold tracking-tight text-foreground">
        Analyze customer reviews
      </h1>
      <p className="mt-2 text-sm text-muted-foreground">
        Paste a Google Maps link to a business and ReviewLens will collect its reviews.
      </p>

      <form onSubmit={handleSubmit} className="mt-8 space-y-3" noValidate>
        <div className="flex flex-col gap-3 sm:flex-row">
          <Input
            type="url"
            value={url}
            onChange={(event) => {
              setUrl(event.target.value)
              setError(null)
            }}
            placeholder="https://www.google.com/maps/place/..."
            aria-label="Google Maps URL"
            aria-invalid={error !== null}
            className="h-11 flex-1"
          />
          <Button type="submit" size="lg" disabled={createTarget.isPending}>
            {createTarget.isPending ? (
              <Loader2 className="size-4 animate-spin" />
            ) : (
              <Search className="size-4" />
            )}
            Analyze Reviews
          </Button>
        </div>

        {error ? (
          <p role="alert" className="text-sm text-destructive">
            {error}
          </p>
        ) : null}
      </form>
    </div>
  )
}
