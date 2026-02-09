import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { FinancialChart } from '@/components/analysis'
import { CompetitorAnalysisView } from '@/components/analysis'
import { InventoryRecommendations } from '@/components/analysis'
import { KPIDashboard } from '@/components/analysis'
import { RecommendationsPanel } from '@/components/feedback'
import { CompareDesigns } from '@/components/compare-designs'
import { FeedbackSection } from '@/components/feedback'
import type { StoreDesign } from '@/types'

interface DesignAnalysisProps {
  design: StoreDesign
  storeId: string
  analysis?: Record<string, unknown>
  designsData?: { items: StoreDesign[] }
}

export function DesignAnalysis({
  design,
  storeId,
  analysis,
  designsData,
}: DesignAnalysisProps) {
  return (
    <div className="space-y-4">
      <FinancialChart design={design} />
      <CompetitorAnalysisView design={design} />
      {design.inventory_recommendations && (
        <InventoryRecommendations design={design} />
      )}
      {design.kpis && <KPIDashboard design={design} />}
      <RecommendationsPanel storeId={storeId} />
      {designsData?.items && designsData.items.length > 1 && (
        <CompareDesigns
          currentDesignId={storeId}
          designs={designsData.items}
        />
      )}
      <FeedbackSection storeId={storeId} />
      {analysis && (
        <Card>
          <CardHeader>
            <CardTitle>Análisis Completo (JSON)</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="bg-gray-50 p-4 rounded-lg overflow-auto text-xs">
              {JSON.stringify(analysis, null, 2)}
            </pre>
          </CardContent>
        </Card>
      )}
    </div>
  )
}


