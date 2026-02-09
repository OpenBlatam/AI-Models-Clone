import { useCallback } from 'react'
import { useToast } from '@/components/ui/toast'
import { getErrorMessage } from '@/lib/error-handler'

export function useErrorHandler() {
  const { showToast } = useToast()

  const handleError = useCallback(
    (error: unknown, defaultMessage = 'Ocurrió un error') => {
      const message = getErrorMessage(error) || defaultMessage
      showToast(message, 'error')
      return message
    },
    [showToast]
  )

  return { handleError }
}


