import { Component, type ErrorInfo, type ReactNode } from 'react'

import { Button } from '@/components/ui/button'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
}

/** Last line of defence: a render crash must never show a stack trace. */
export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false }

  static getDerivedStateFromError(): State {
    return { hasError: true }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('Unhandled UI error', error, info.componentStack)
  }

  render() {
    if (!this.state.hasError) return this.props.children

    return (
      <div className="mx-auto max-w-xl px-4 py-24 text-center">
        <h1 className="text-lg font-semibold text-foreground">Something went wrong</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          ReviewLens ran into an unexpected problem. Reloading usually fixes it.
        </p>
        <Button className="mt-6" onClick={() => window.location.reload()}>
          Reload ReviewLens
        </Button>
      </div>
    )
  }
}
