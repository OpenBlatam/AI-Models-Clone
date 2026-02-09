import { Alert } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'

interface ErrorMessageProps {
  message: string
  onRetry?: () => void
  retryLabel?: string
}

export function ErrorMessage({
  message,
  onRetry,
  retryLabel = 'Reintentar',
}: ErrorMessageProps) {
  return (
    <div className="space-y-4">
      <Alert variant="destructive" title="Error">
        {message}
      </Alert>
      {onRetry && (
        <div className="flex justify-center">
          <Button onClick={onRetry}>{retryLabel}</Button>
        </div>
      )}
    </div>
  )
}


