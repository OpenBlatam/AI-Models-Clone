import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

export function useAnalysis(storeId: string) {
  return useQuery({
    queryKey: ['analysis', storeId],
    queryFn: () => apiClient.getFullAnalysis(storeId),
    enabled: !!storeId,
  })
}

export function useCompetitorAnalysis(storeId: string) {
  return useQuery({
    queryKey: ['competitor-analysis', storeId],
    queryFn: () => apiClient.getCompetitorAnalysis(storeId),
    enabled: !!storeId,
  })
}

export function useFinancialAnalysis(storeId: string) {
  return useQuery({
    queryKey: ['financial-analysis', storeId],
    queryFn: () => apiClient.getFinancialAnalysis(storeId),
    enabled: !!storeId,
  })
}

export function useKPIs(storeId: string) {
  return useQuery({
    queryKey: ['kpis', storeId],
    queryFn: () => apiClient.getKPIs(storeId),
    enabled: !!storeId,
  })
}


