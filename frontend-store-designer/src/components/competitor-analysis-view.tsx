'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Alert } from '@/components/ui/alert'
import { TrendingUp, TrendingDown, AlertTriangle } from 'lucide-react'
import type { StoreDesign } from '@/types'

interface CompetitorAnalysisViewProps {
  design: StoreDesign
}

export function CompetitorAnalysisView({ design }: CompetitorAnalysisViewProps) {
  if (!design.competitor_analysis) return null

  const analysis = design.competitor_analysis as Record<string, unknown>

  return (
    <Card>
      <CardHeader>
        <CardTitle>Análisis de Competencia</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {analysis.competitors && (
          <div>
            <h4 className="font-medium text-sm mb-2">Competidores Identificados</h4>
            <div className="space-y-2">
              {(analysis.competitors as Array<Record<string, unknown>>).map(
                (competitor, idx) => (
                  <div
                    key={idx}
                    className="p-3 bg-gray-50 rounded-lg border border-gray-200"
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="font-medium text-sm">
                          {competitor.name || `Competidor ${idx + 1}`}
                        </p>
                        {competitor.distance && (
                          <p className="text-xs text-gray-600 mt-1">
                            A {competitor.distance} de distancia
                          </p>
                        )}
                      </div>
                      {competitor.rating && (
                        <Badge variant="outline">
                          ⭐ {String(competitor.rating)}
                        </Badge>
                      )}
                    </div>
                  </div>
                )
              )}
            </div>
          </div>
        )}

        {analysis.market_opportunities && (
          <div>
            <h4 className="font-medium text-sm mb-2 flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-green-600" />
              Oportunidades de Mercado
            </h4>
            <ul className="space-y-1">
              {(analysis.market_opportunities as string[]).map((opp, idx) => (
                <li key={idx} className="text-sm text-gray-700">
                  • {opp}
                </li>
              ))}
            </ul>
          </div>
        )}

        {analysis.threats && (
          <div>
            <h4 className="font-medium text-sm mb-2 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-red-600" />
              Amenazas
            </h4>
            <Alert variant="warning">
              <ul className="space-y-1">
                {(analysis.threats as string[]).map((threat, idx) => (
                  <li key={idx} className="text-sm">• {threat}</li>
                ))}
              </ul>
            </Alert>
          </div>
        )}

        {analysis.competitive_advantages && (
          <div>
            <h4 className="font-medium text-sm mb-2">Ventajas Competitivas</h4>
            <div className="flex flex-wrap gap-2">
              {(analysis.competitive_advantages as string[]).map((adv, idx) => (
                <Badge key={idx} variant="secondary">
                  {adv}
                </Badge>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}


