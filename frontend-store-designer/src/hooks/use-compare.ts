import { useMutation } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/components/ui/toast'

export function useCompareDesigns() {
  const { showToast } = useToast()

  return useMutation({
    mutationFn: (ids: string[]) => apiClient.compareDesigns(ids),
    onSuccess: () => {
      showToast('Comparación generada', 'success')
    },
    onError: (error: Error) => {
      showToast(error.message || 'Error al comparar', 'error')
    },
  })
}


