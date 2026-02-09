'use client'

import { useRecommendations } from '@/hooks/use-recommendations'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Lightbulb } from 'lucide-react'

interface RecommendationsPanelProps {
  storeId: string
}

export function RecommendationsPanel({ storeId }: RecommendationsPanelProps) {
  const { data: recommendations, isLoading } = useRecommendations(storeId)

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-48" />
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-4 w-1/2" />
          </div>
        </CardContent>
      </Card>
    )
  }

  if (!recommendations) {
    return null
  }

  const recs = recommendations as Record<string, unknown>

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Lightbulb className="w-5 h-5 text-yellow-500" />
          Recomendaciones Inteligentes
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {recs.immediate_actions && (
            <div>
              <h4 className="font-medium text-sm mb-2">Acciones Inmediatas:</h4>
              <ul className="list-disc list-inside space-y-1 text-sm text-gray-600">
                {(recs.immediate_actions as string[]).map((action, idx) => (
                  <li key={idx}>{action}</li>
                ))}
              </ul>
            </div>
          )}
          {recs.optimizations && (
            <div>
              <h4 className="font-medium text-sm mb-2">Optimizaciones:</h4>
              <ul className="list-disc list-inside space-y-1 text-sm text-gray-600">
                {(recs.optimizations as string[]).map((opt, idx) => (
                  <li key={idx}>{opt}</li>
                ))}
              </ul>
            </div>
          )}
          {recs.risk_alerts && (
            <div>
              <h4 className="font-medium text-sm mb-2 text-red-600">Alertas:</h4>
              <ul className="list-disc list-inside space-y-1 text-sm text-red-600">
                {(recs.risk_alerts as string[]).map((alert, idx) => (
                  <li key={idx}>{alert}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

