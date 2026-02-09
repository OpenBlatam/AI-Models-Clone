'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Package } from 'lucide-react'
import type { StoreDesign } from '@/types'

interface InventoryRecommendationsProps {
  design: StoreDesign
}

export function InventoryRecommendations({ design }: InventoryRecommendationsProps) {
  if (!design.inventory_recommendations) return null

  const inventory = design.inventory_recommendations as Record<string, unknown>

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Package className="w-5 h-5" />
          Recomendaciones de Inventario
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {inventory.categories && (
            <div>
              <h4 className="font-medium text-sm mb-2">Categorías Principales</h4>
              <div className="flex flex-wrap gap-2">
                {(inventory.categories as string[]).map((cat, idx) => (
                  <Badge key={idx} variant="secondary">
                    {cat}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {inventory.initial_stock && (
            <div>
              <h4 className="font-medium text-sm mb-2">Stock Inicial Recomendado</h4>
              <div className="space-y-2">
                {Object.entries(inventory.initial_stock as Record<string, number>).map(
                  ([item, quantity]) => (
                    <div
                      key={item}
                      className="flex justify-between items-center p-2 bg-gray-50 rounded"
                    >
                      <span className="text-sm">{item}</span>
                      <Badge>{quantity} unidades</Badge>
                    </div>
                  )
                )}
              </div>
            </div>
          )}

          {inventory.reorder_points && (
            <div>
              <h4 className="font-medium text-sm mb-2">Puntos de Reorden</h4>
              <div className="space-y-1">
                {Object.entries(inventory.reorder_points as Record<string, number>).map(
                  ([item, point]) => (
                    <div key={item} className="text-sm">
                      <span className="font-medium">{item}:</span>{' '}
                      <span className="text-gray-600">Reordenar a {point} unidades</span>
                    </div>
                  )
                )}
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}


