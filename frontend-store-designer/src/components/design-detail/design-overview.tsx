import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { LayoutVisualizer } from '@/components/visualization'
import { VisualizationGallery } from '@/components/visualization'
import { KPIDashboard } from '@/components/analysis'
import { InventoryRecommendations } from '@/components/analysis'
import type { StoreDesign } from '@/types'

interface DesignOverviewProps {
  design: StoreDesign
}

export function DesignOverview({ design }: DesignOverviewProps) {
  return (
    <div className="space-y-4">
      <LayoutVisualizer layout={design.layout} />
      <VisualizationGallery visualizations={design.visualizations} />
      {design.kpis && <KPIDashboard design={design} />}
      {design.inventory_recommendations && (
        <InventoryRecommendations design={design} />
      )}
    </div>
  )
}


