import { ArrowRight, Loader2 } from 'lucide-react'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useCreateAnalysisTarget } from '@/hooks/useAnalysis'
import { startUrlIngestion } from '@/lib/api/analysisTargets'
import { ApiError } from '@/lib/api/client'
import { useApiToken } from '@/hooks/useApiToken'
import { deriveWorkingName, detectSourcePlatform, validateSourceUrl } from '@/lib/sourceUrl'

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
  const detectedPlatform = detectSourcePlatform(url)

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
      <form onSubmit={handleSubmit} className="mt-8 space-y-3" noValidate>
        <div className="grid grid-cols-[minmax(0,1fr)_auto] items-end gap-x-3 gap-y-2">
          <div className="min-w-0 flex-1 space-y-2">
            <Label htmlFor="source-url">URL</Label>
            <Input
              id="source-url"
              type="url"
              value={url}
              onChange={(event) => {
                setUrl(event.target.value)
                setError(null)
              }}
              placeholder="Paste a source URL"
              aria-invalid={error !== null}
              aria-describedby={error ? 'source-url-hint source-url-error' : 'source-url-hint'}
              className="h-11"
            />
          </div>
          <Button
            type="submit"
            variant="default"
            size="icon-lg"
            className="size-11"
            disabled={createTarget.isPending}
            aria-label="Start analysis"
            title="Start analysis"
          >
            {createTarget.isPending ? (
              <Loader2 className="size-4 animate-spin" />
            ) : (
              <ArrowRight className="size-4" />
            )}
          </Button>
          <p id="source-url-hint" className="col-span-2 text-xs text-muted-foreground">
            Paste a Google Maps place or Amazon.com product URL.
            {detectedPlatform ? (
              <span className="ml-2 font-medium text-foreground" aria-live="polite">
                Detected: {detectedPlatform === 'amazon' ? 'Amazon' : 'Google Maps'}
              </span>
            ) : null}
          </p>
        </div>

        {error ? (
          <p id="source-url-error" role="alert" className="text-sm text-destructive">
            {error}
          </p>
        ) : null}
      </form>
    </div>
  )
}
