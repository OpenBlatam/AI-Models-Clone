'use client'

import { Button } from '@/components/ui/button'
import { Download, Share2, Edit, Copy } from 'lucide-react'
import { useToast } from '@/components/ui/toast'

interface QuickActionsProps {
  storeId: string
  onExport?: (format: 'json' | 'markdown' | 'html') => void
  onShare?: () => void
  onEdit?: () => void
}

export function QuickActions({
  storeId,
  onExport,
  onShare,
  onEdit,
}: QuickActionsProps) {
  const { showToast } = useToast()

  const handleCopyLink = async () => {
    const url = `${window.location.origin}/designs/${storeId}`
    try {
      await navigator.clipboard.writeText(url)
      showToast('Enlace copiado', 'success')
    } catch {
      showToast('Error al copiar', 'error')
    }
  }

  return (
    <div className="flex flex-wrap gap-2">
      {onEdit && (
        <Button variant="outline" size="sm" onClick={onEdit}>
          <Edit className="w-4 h-4 mr-2" />
          Editar
        </Button>
      )}
      {onShare && (
        <Button variant="outline" size="sm" onClick={onShare}>
          <Share2 className="w-4 h-4 mr-2" />
          Compartir
        </Button>
      )}
      <Button variant="outline" size="sm" onClick={handleCopyLink}>
        <Copy className="w-4 h-4 mr-2" />
        Copiar Enlace
      </Button>
      {onExport && (
        <>
          <Button
            variant="outline"
            size="sm"
            onClick={() => onExport('json')}
          >
            <Download className="w-4 h-4 mr-2" />
            JSON
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => onExport('markdown')}
          >
            <Download className="w-4 h-4 mr-2" />
            MD
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => onExport('html')}
          >
            <Download className="w-4 h-4 mr-2" />
            HTML
          </Button>
        </>
      )}
    </div>
  )
}


