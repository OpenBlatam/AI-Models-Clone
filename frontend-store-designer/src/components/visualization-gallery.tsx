'use client'

import { useState } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Image as ImageIcon, ZoomIn, Download } from 'lucide-react'
import type { StoreVisualization } from '@/types'

interface VisualizationGalleryProps {
  visualizations: StoreVisualization[]
}

export function VisualizationGallery({ visualizations }: VisualizationGalleryProps) {
  const [selectedIndex, setSelectedIndex] = useState(0)

  if (visualizations.length === 0) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <ImageIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">No hay visualizaciones disponibles</p>
        </CardContent>
      </Card>
    )
  }

  const selected = visualizations[selectedIndex]

  return (
    <Card>
      <CardContent className="p-6">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">Visualizaciones</h3>
            <div className="flex gap-2">
              <Button variant="outline" size="sm">
                <Download className="w-4 h-4 mr-2" />
                Descargar
              </Button>
            </div>
          </div>

          {selected.image_url ? (
            <div className="relative aspect-video bg-gray-100 rounded-lg overflow-hidden">
              <img
                src={selected.image_url}
                alt={selected.view_type}
                className="w-full h-full object-cover"
              />
              <div className="absolute inset-0 bg-black/0 hover:bg-black/10 transition-colors flex items-center justify-center">
                <ZoomIn className="w-8 h-8 text-white opacity-0 hover:opacity-100 transition-opacity" />
              </div>
            </div>
          ) : (
            <div className="aspect-video bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg flex items-center justify-center border-2 border-dashed border-gray-300">
              <div className="text-center">
                <ImageIcon className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                <p className="text-sm text-gray-600">Imagen no disponible</p>
                <p className="text-xs text-gray-500 mt-1">{selected.image_prompt}</p>
              </div>
            </div>
          )}

          <div>
            <p className="text-sm font-medium mb-2">
              {selected.view_type.charAt(0).toUpperCase() + selected.view_type.slice(1)}
            </p>
            <p className="text-xs text-gray-600">{selected.image_prompt}</p>
          </div>

          {visualizations.length > 1 && (
            <div className="flex gap-2 overflow-x-auto pb-2">
              {visualizations.map((viz, idx) => (
                <button
                  key={idx}
                  onClick={() => setSelectedIndex(idx)}
                  className={`flex-shrink-0 w-20 h-20 rounded-lg border-2 overflow-hidden ${
                    selectedIndex === idx
                      ? 'border-blue-600'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  {viz.image_url ? (
                    <img
                      src={viz.image_url}
                      alt={viz.view_type}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full bg-gray-100 flex items-center justify-center">
                      <ImageIcon className="w-6 h-6 text-gray-400" />
                    </div>
                  )}
                </button>
              ))}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}


