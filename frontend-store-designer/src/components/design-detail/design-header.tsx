'use client'

import { Button } from '@/components/ui/button'
import { CopyButton, QuickActions } from '@/components/actions'
import { ConfirmModal } from '@/components/ui/modal'
import { Trash2 } from 'lucide-react'
import { formatDate } from '@/lib/utils'
import type { StoreDesign } from '@/types'

interface DesignHeaderProps {
  design: StoreDesign
  storeId: string
  onExport: (format: 'json' | 'markdown' | 'html') => void
  onDelete: () => void
  isExporting: boolean
  isDeleting: boolean
  showDeleteModal: boolean
  setShowDeleteModal: (show: boolean) => void
}

export function DesignHeader({
  design,
  storeId,
  onExport,
  onDelete,
  isExporting,
  isDeleting,
  showDeleteModal,
  setShowDeleteModal,
}: DesignHeaderProps) {
  return (
    <>
      <div className="mb-6 flex justify-between items-start">
        <div className="flex-1">
          <h1 className="text-4xl font-bold mb-2">{design.store_name}</h1>
          <div className="flex items-center gap-4 text-gray-600">
            <p>Creado el {formatDate(design.created_at)}</p>
            <CopyButton text={storeId} label="ID" size="sm" />
          </div>
        </div>
        <div className="flex gap-2">
          <QuickActions storeId={storeId} onExport={onExport} />
          <Button
            variant="destructive"
            size="sm"
            onClick={() => setShowDeleteModal(true)}
            disabled={isDeleting}
          >
            <Trash2 className="w-4 h-4 mr-2" />
            Eliminar
          </Button>
        </div>
      </div>

      <ConfirmModal
        isOpen={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        onConfirm={onDelete}
        title="Eliminar Diseño"
        message="¿Estás seguro de que deseas eliminar este diseño? Esta acción no se puede deshacer."
        confirmLabel="Eliminar"
        cancelLabel="Cancelar"
        variant="destructive"
      />
    </>
  )
}


