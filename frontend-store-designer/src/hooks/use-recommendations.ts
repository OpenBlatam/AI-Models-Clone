import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

export function useRecommendations(storeId: string) {
  return useQuery({
    queryKey: ['recommendations', storeId],
    queryFn: () => apiClient.getRecommendations(storeId),
    enabled: !!storeId,
  })
}


