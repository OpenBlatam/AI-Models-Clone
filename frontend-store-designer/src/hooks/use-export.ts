import { useMutation } from '@tanstack/react-query'
import { useExportDesign } from './use-designs'
import { downloadFile, getExportFilename } from '@/services/export-service'
import { useToast } from '@/components/ui/toast'

export function useExport(storeId: string) {
  const { showToast } = useToast()
  const exportMutation = useExportDesign()

  const exportDesign = (format: 'json' | 'markdown' | 'html') => {
    exportMutation.mutate(
      { storeId, format },
      {
        onSuccess: (blob) => {
          downloadFile(blob, getExportFilename(storeId, format))
          showToast('Diseño exportado', 'success')
        },
        onError: (error: Error) => {
          showToast(error.message || 'Error al exportar', 'error')
        },
      }
    )
  }

  return {
    exportDesign,
    isExporting: exportMutation.isPending,
  }
}


