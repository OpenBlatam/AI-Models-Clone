'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useCompareDesigns } from '@/hooks/use-compare'
import { useToast } from '@/components/ui/toast'
import { Compare, Loader2 } from 'lucide-react'
import { Checkbox } from '@/components/ui/checkbox'
import type { StoreDesign } from '@/types'

interface CompareDesignsProps {
  currentDesignId: string
  designs: StoreDesign[]
}

export function CompareDesigns({ currentDesignId, designs }: CompareDesignsProps) {
  const [selectedIds, setSelectedIds] = useState<string[]>([])
  const { showToast } = useToast()
  const compareMutation = useCompareDesigns()

  const handleCompare = () => {
    if (selectedIds.length < 1) {
      showToast('Selecciona al menos 1 diseño', 'warning')
      return
    }
    compareMutation.mutate([currentDesignId, ...selectedIds])
  }

  const toggleDesign = (designId: string) => {
    setSelectedIds((prev) =>
      prev.includes(designId)
        ? prev.filter((id) => id !== designId)
        : [...prev, designId]
    )
  }

  const availableDesigns = designs.filter((d) => d.store_id !== currentDesignId)

  if (availableDesigns.length === 0) {
    return null
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Compare className="w-5 h-5" />
          Comparar Diseños
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2">
            Selecciona diseños para comparar
          </label>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {availableDesigns.map((design) => (
              <label
                key={design.store_id}
                className="flex items-center gap-2 p-2 hover:bg-gray-50 rounded cursor-pointer"
              >
                <Checkbox
                  checked={selectedIds.includes(design.store_id)}
                  onChange={() => toggleDesign(design.store_id)}
                />
                <span className="text-sm">{design.store_name}</span>
              </label>
            ))}
          </div>
        </div>
        <Button
          onClick={handleCompare}
          disabled={compareMutation.isPending || selectedIds.length < 1}
          className="w-full"
        >
          {compareMutation.isPending ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Comparando...
            </>
          ) : (
            <>
              <Compare className="w-4 h-4 mr-2" />
              Comparar ({selectedIds.length + 1} diseños)
            </>
          )}
        </Button>
        {compareMutation.data && (
          <div className="mt-4 p-4 bg-gray-50 rounded-lg">
            <pre className="text-xs overflow-auto">
              {JSON.stringify(compareMutation.data, null, 2)}
            </pre>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

