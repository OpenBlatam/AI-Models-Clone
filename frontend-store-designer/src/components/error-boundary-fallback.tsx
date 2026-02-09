'use client'

import { ErrorBoundary } from 'react-error-boundary'
import { ErrorMessage } from './error-message'
import { Button } from './ui/button'

interface ErrorFallbackProps {
  error: Error
  resetErrorBoundary: () => void
}

function ErrorFallback({ error, resetErrorBoundary }: ErrorFallbackProps) {
  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="text-center max-w-md">
        <ErrorMessage message={error.message || 'Algo salió mal'} />
        <Button onClick={resetErrorBoundary} className="mt-4">
          Intentar de nuevo
        </Button>
      </div>
    </div>
  )
}

interface ErrorBoundaryWrapperProps {
  children: React.ReactNode
}

export function ErrorBoundaryWrapper({ children }: ErrorBoundaryWrapperProps) {
  return (
    <ErrorBoundary FallbackComponent={ErrorFallback}>
      {children}
    </ErrorBoundary>
  )
}


