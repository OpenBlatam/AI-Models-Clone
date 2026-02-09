import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

export function useFeedback(storeId: string) {
  return useQuery({
    queryKey: ['feedback', storeId],
    queryFn: () => apiClient.getFeedback(storeId),
    enabled: !!storeId,
  })
}

export function useAddFeedback(storeId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (feedback: string) => apiClient.addFeedback(storeId, feedback),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['feedback', storeId] })
    },
  })
}


