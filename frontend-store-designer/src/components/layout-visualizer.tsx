'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Ruler } from 'lucide-react'
import type { StoreLayout } from '@/types'

interface LayoutVisualizerProps {
  layout: StoreLayout
}

export function LayoutVisualizer({ layout }: LayoutVisualizerProps) {
  const { width, length, height } = layout.dimensions
  const scale = 200 / Math.max(width, length)
  const scaledWidth = width * scale
  const scaledLength = length * scale

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Ruler className="w-5 h-5" />
          Visualización del Layout
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex gap-4 text-sm">
            <div>
              <span className="font-medium">Ancho:</span> {width}m
            </div>
            <div>
              <span className="font-medium">Largo:</span> {length}m
            </div>
            <div>
              <span className="font-medium">Alto:</span> {height}m
            </div>
            <div>
              <span className="font-medium">Área:</span>{' '}
              {(width * length).toFixed(2)}m²
            </div>
          </div>

          <div className="border-2 border-gray-300 rounded-lg p-4 bg-gray-50">
            <svg
              width="100%"
              height={scaledLength + 40}
              viewBox={`0 0 ${scaledWidth + 40} ${scaledLength + 40}`}
              className="max-w-full"
            >
              <rect
                x="20"
                y="20"
                width={scaledWidth}
                height={scaledLength}
                fill="white"
                stroke="#3b82f6"
                strokeWidth="2"
                rx="4"
              />
              {layout.zones.map((zone, idx) => (
                <g key={idx}>
                  {zone.position && (
                    <rect
                      x={20 + (zone.position.x || 0) * scale}
                      y={20 + (zone.position.y || 0) * scale}
                      width={(zone.width || 0) * scale}
                      height={(zone.length || 0) * scale}
                      fill="#dbeafe"
                      stroke="#3b82f6"
                      strokeWidth="1"
                      opacity="0.6"
                    />
                  )}
                </g>
              ))}
              {layout.furniture_placement.map((furniture, idx) => (
                <circle
                  key={idx}
                  cx={20 + (furniture.x || 0) * scale}
                  cy={20 + (furniture.y || 0) * scale}
                  r="4"
                  fill="#10b981"
                  opacity="0.7"
                />
              ))}
            </svg>
          </div>

          {layout.zones.length > 0 && (
            <div>
              <h4 className="font-medium text-sm mb-2">Zonas:</h4>
              <div className="grid grid-cols-2 gap-2">
                {layout.zones.map((zone, idx) => (
                  <div key={idx} className="text-sm p-2 bg-blue-50 rounded">
                    {zone.name || `Zona ${idx + 1}`}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}


