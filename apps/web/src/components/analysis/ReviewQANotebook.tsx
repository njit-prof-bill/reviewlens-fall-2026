import { CircleAlert, MessageSquareText, Send, Star } from 'lucide-react'
import { useState, type FormEvent } from 'react'

import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { useAskTargetQuestion, useTargetQuestions } from '@/hooks/useAnalysis'
import { ApiError } from '@/lib/api/client'
import type { QAEntry } from '@/lib/api/types'

const SUGGESTED_QUESTIONS = [
  'What do customers like most?',
  'What complaints appear repeatedly?',
  'What themes explain the ratings?',
]

function Evidence({ entry }: { entry: QAEntry }) {
  if (entry.evidence.length === 0) return null
  return (
    <div className="space-y-2">
      <p className="text-xs font-medium uppercase text-muted-foreground">Supporting reviews</p>
      {entry.evidence.map((item, index) => (
        <blockquote
          key={`${entry.id}-${item.review_id ?? index}`}
          className="border-l-2 border-border pl-3 text-sm text-muted-foreground"
        >
          <p className="break-words">“{item.excerpt}”</p>
          <footer className="mt-1 flex flex-wrap items-center gap-2 text-xs">
            <span>{item.reviewer_name ?? 'Google Maps reviewer'}</span>
            {item.rating !== null ? (
              <span className="inline-flex items-center gap-1" aria-label={`${item.rating} stars`}>
                <Star className="size-3 fill-current" aria-hidden="true" />
                {item.rating.toFixed(1)}
              </span>
            ) : null}
          </footer>
        </blockquote>
      ))}
    </div>
  )
}

function NotebookEntry({ entry }: { entry: QAEntry }) {
  const isGrounded = entry.result_kind === 'grounded'
  return (
    <article className="space-y-3" aria-label={`Question: ${entry.question}`}>
      <div className="flex items-start gap-3">
        <MessageSquareText className="mt-0.5 size-4 shrink-0 text-muted-foreground" />
        <p className="min-w-0 break-words text-sm font-medium">{entry.question}</p>
      </div>
      {isGrounded ? (
        <Card className="rounded-lg">
          <CardHeader>
            <CardTitle className="text-sm">Analysis</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="break-words text-sm leading-6">{entry.answer}</p>
            <Evidence entry={entry} />
          </CardContent>
        </Card>
      ) : (
        <Alert>
          <CircleAlert className="size-4" />
          <AlertTitle>
            {entry.result_kind === 'out_of_scope' ? 'Outside this analysis' : 'Not enough evidence'}
          </AlertTitle>
          <AlertDescription>{entry.answer}</AlertDescription>
        </Alert>
      )}
    </article>
  )
}

interface ReviewQANotebookProps {
  targetId: string
  targetName: string
  enabled: boolean
}

export function ReviewQANotebook({ targetId, targetName, enabled }: ReviewQANotebookProps) {
  const history = useTargetQuestions(targetId)
  const askQuestion = useAskTargetQuestion(targetId)
  const [question, setQuestion] = useState('')

  async function submit(event: FormEvent) {
    event.preventDefault()
    const trimmed = question.trim()
    if (!trimmed || !enabled || askQuestion.isPending) return
    try {
      await askQuestion.mutateAsync(trimmed)
      setQuestion('')
    } catch {
      // The mutation state renders the user-safe API error below the form.
    }
  }

  if (!enabled) {
    return (
      <Alert>
        <CircleAlert className="size-4" />
        <AlertTitle>Reviews required</AlertTitle>
        <AlertDescription>
          Complete review ingestion for {targetName} before asking questions.
        </AlertDescription>
      </Alert>
    )
  }

  const errorMessage =
    askQuestion.error instanceof ApiError
      ? askQuestion.error.displayMessage
      : askQuestion.isError
        ? 'The question could not be answered. Please try again.'
        : null

  return (
    <div className="space-y-5">
      {history.isPending ? (
        <div className="space-y-3" aria-label="Loading question history">
          <Skeleton className="h-5 w-2/3" />
          <Skeleton className="h-28 w-full" />
        </div>
      ) : null}

      {history.data?.items.map((entry) => <NotebookEntry key={entry.id} entry={entry} />)}

      {history.isError ? (
        <Alert variant="destructive">
          <CircleAlert className="size-4" />
          <AlertTitle>Question history unavailable</AlertTitle>
          <AlertDescription>Refresh the page to try loading it again.</AlertDescription>
        </Alert>
      ) : null}

      <form className="space-y-3" onSubmit={(event) => void submit(event)}>
        <label htmlFor="review-question" className="text-sm font-medium">
          Ask about {targetName}
        </label>
        <div className="flex items-center gap-2">
          <Input
            id="review-question"
            value={question}
            maxLength={500}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Ask a question about these reviews"
            disabled={askQuestion.isPending}
          />
          <Button
            type="submit"
            size="icon"
            disabled={!question.trim() || askQuestion.isPending}
            aria-label={askQuestion.isPending ? 'Answering question' : 'Ask question'}
          >
            <Send className="size-4" aria-hidden="true" />
          </Button>
        </div>
        <div className="flex flex-wrap gap-2" aria-label="Suggested questions">
          {SUGGESTED_QUESTIONS.map((suggestion) => (
            <Button
              key={suggestion}
              type="button"
              size="sm"
              variant="outline"
              onClick={() => setQuestion(suggestion)}
              disabled={askQuestion.isPending}
            >
              {suggestion}
            </Button>
          ))}
        </div>
        {askQuestion.isPending ? <Badge variant="secondary">Analyzing reviews...</Badge> : null}
        {errorMessage ? (
          <Alert variant="destructive">
            <CircleAlert className="size-4" />
            <AlertTitle>Question not answered</AlertTitle>
            <AlertDescription>{errorMessage}</AlertDescription>
          </Alert>
        ) : null}
      </form>
    </div>
  )
}