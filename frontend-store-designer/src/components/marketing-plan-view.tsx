import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Megaphone } from 'lucide-react'
import type { MarketingPlan } from '@/types'

interface MarketingPlanViewProps {
  plan: MarketingPlan
}

export function MarketingPlanView({ plan }: MarketingPlanViewProps) {
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Megaphone className="w-5 h-5" />
            Plan de Marketing
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h3 className="font-semibold mb-2">Audiencia Objetivo</h3>
            <p className="text-gray-700">{plan.target_audience}</p>
          </div>

          {plan.marketing_strategy.length > 0 && (
            <div>
              <h3 className="font-semibold mb-2">Estrategias de Marketing</h3>
              <ul className="space-y-2">
                {plan.marketing_strategy.map((strategy, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="text-blue-600 mt-1">•</span>
                    <span className="text-gray-700">{strategy}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {plan.sales_tactics.length > 0 && (
            <div>
              <h3 className="font-semibold mb-2">Tácticas de Ventas</h3>
              <div className="flex flex-wrap gap-2">
                {plan.sales_tactics.map((tactic, idx) => (
                  <Badge key={idx} variant="secondary">
                    {tactic}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          <div>
            <h3 className="font-semibold mb-2">Estrategia de Precios</h3>
            <p className="text-gray-700">{plan.pricing_strategy}</p>
          </div>

          {plan.promotion_ideas.length > 0 && (
            <div>
              <h3 className="font-semibold mb-2">Ideas de Promoción</h3>
              <ul className="space-y-1">
                {plan.promotion_ideas.map((idea, idx) => (
                  <li key={idx} className="text-sm text-gray-600">
                    • {idea}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {plan.opening_strategy && (
            <div>
              <h3 className="font-semibold mb-2">Estrategia de Apertura</h3>
              <p className="text-gray-700">{plan.opening_strategy}</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}


