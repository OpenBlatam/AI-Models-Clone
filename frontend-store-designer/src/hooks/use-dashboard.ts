import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

export function useDashboard() {
  return useQuery({
    queryKey: ['dashboard'],
    queryFn: () => apiClient.getDashboard(),
  })
}


