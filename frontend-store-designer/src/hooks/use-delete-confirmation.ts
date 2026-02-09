import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useDeleteDesign } from './use-designs'
import { useToast } from '@/components/ui/toast'

export function useDeleteConfirmation(storeId: string, redirectPath = '/designs') {
  const [showModal, setShowModal] = useState(false)
  const router = useRouter()
  const { showToast } = useToast()
  const deleteMutation = useDeleteDesign()

  const handleDelete = () => {
    deleteMutation.mutate(storeId, {
      onSuccess: () => {
        showToast('Diseño eliminado', 'success')
        router.push(redirectPath)
      },
      onError: (error: Error) => {
        showToast(error.message || 'Error al eliminar', 'error')
      },
    })
  }

  return {
    showModal,
    setShowModal,
    handleDelete,
    isDeleting: deleteMutation.isPending,
  }
}


