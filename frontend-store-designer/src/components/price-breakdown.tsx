import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { formatCurrency } from '@/lib/utils'
import { DollarSign } from 'lucide-react'
import type { DecorationPlan } from '@/types'

interface PriceBreakdownProps {
  plan: DecorationPlan
}

export function PriceBreakdown({ plan }: PriceBreakdownProps) {
  const total = Object.values(plan.budget_estimate).reduce(
    (sum, val) => sum + val,
    0
  )
  const items = Object.entries(plan.budget_estimate).sort(
    (a, b) => b[1] - a[1]
  )

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <DollarSign className="w-5 h-5" />
          Desglose de Presupuesto
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {items.map(([category, amount]) => {
            const percentage = (amount / total) * 100
            return (
              <div key={category} className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span className="font-medium">{category}</span>
                  <span>{formatCurrency(amount)}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all"
                    style={{ width: `${percentage}%` }}
                  />
                </div>
                <div className="text-xs text-gray-500 text-right">
                  {percentage.toFixed(1)}%
                </div>
              </div>
            )
          })}
          <div className="pt-3 border-t flex justify-between items-center font-semibold">
            <span>Total</span>
            <span className="text-lg">{formatCurrency(total)}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}


