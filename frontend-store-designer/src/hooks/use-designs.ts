import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import type { StoreDesign, StoreDesignRequest } from '@/types'

export function useDesigns(page = 1, pageSize = 100) {
  return useQuery({
    queryKey: ['designs', page, pageSize],
    queryFn: () => apiClient.listDesigns(page, pageSize),
  })
}

export function useDesign(storeId: string) {
  return useQuery({
    queryKey: ['design', storeId],
    queryFn: () => apiClient.getDesign(storeId),
    enabled: !!storeId,
  })
}

export function useCreateDesign() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: StoreDesignRequest) => apiClient.generateDesign(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['designs'] })
    },
  })
}

export function useDeleteDesign() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (storeId: string) => apiClient.deleteDesign(storeId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['designs'] })
    },
  })
}

export function useExportDesign() {
  return useMutation({
    mutationFn: ({
      storeId,
      format,
    }: {
      storeId: string
      format: 'json' | 'markdown' | 'html'
    }) => apiClient.exportDesign(storeId, format),
  })
}


