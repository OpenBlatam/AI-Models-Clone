import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { formatCurrency } from '@/lib/utils'
import { Palette } from 'lucide-react'
import type { DecorationPlan } from '@/types'

interface DecorationPlanViewProps {
  plan: DecorationPlan
}

export function DecorationPlanView({ plan }: DecorationPlanViewProps) {
  const totalBudget = Object.values(plan.budget_estimate).reduce(
    (sum, val) => sum + val,
    0
  )

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Palette className="w-5 h-5" />
            Plan de Decoración
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div>
            <h3 className="font-semibold mb-3">Esquema de Colores</h3>
            <div className="flex flex-wrap gap-4">
              {Object.entries(plan.color_scheme).map(([key, value]) => (
                <div key={key} className="text-center">
                  <div
                    className="w-20 h-20 rounded-lg border-2 border-gray-200 shadow-sm mb-2"
                    style={{ backgroundColor: value }}
                  />
                  <p className="text-xs font-medium">{key}</p>
                  <p className="text-xs text-gray-500">{value}</p>
                </div>
              ))}
            </div>
          </div>

          <div>
            <h3 className="font-semibold mb-3">Presupuesto Estimado</h3>
            <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-4 rounded-lg">
              <div className="text-3xl font-bold text-blue-700 mb-2">
                {formatCurrency(totalBudget)}
              </div>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mt-3">
                {Object.entries(plan.budget_estimate).map(([key, value]) => (
                  <div
                    key={key}
                    className="flex justify-between items-center p-2 bg-white rounded"
                  >
                    <span className="text-sm text-gray-600">{key}:</span>
                    <span className="text-sm font-semibold">
                      {formatCurrency(value)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {plan.materials.length > 0 && (
            <div>
              <h3 className="font-semibold mb-2">Materiales Recomendados</h3>
              <div className="flex flex-wrap gap-2">
                {plan.materials.map((material, idx) => (
                  <Badge key={idx} variant="outline">
                    {material}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {plan.furniture_recommendations.length > 0 && (
            <div>
              <h3 className="font-semibold mb-2">Recomendaciones de Muebles</h3>
              <div className="space-y-2">
                {plan.furniture_recommendations.slice(0, 5).map((furniture, idx) => (
                  <div
                    key={idx}
                    className="p-3 bg-gray-50 rounded-lg border border-gray-200"
                  >
                    <p className="font-medium text-sm">
                      {furniture.name || `Mueble ${idx + 1}`}
                    </p>
                    {furniture.description && (
                      <p className="text-xs text-gray-600 mt-1">
                        {furniture.description}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {plan.decoration_elements.length > 0 && (
            <div>
              <h3 className="font-semibold mb-2">Elementos Decorativos</h3>
              <ul className="space-y-1">
                {plan.decoration_elements.map((element, idx) => (
                  <li key={idx} className="text-sm text-gray-700">
                    • {element.name || JSON.stringify(element)}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}


