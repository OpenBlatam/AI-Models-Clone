'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { StatCard } from './stat-card'
import { TrendingUp, DollarSign, Users, ShoppingCart } from 'lucide-react'
import type { StoreDesign } from '@/types'

interface KPIDashboardProps {
  design: StoreDesign
}

export function KPIDashboard({ design }: KPIDashboardProps) {
  if (!design.kpis) return null

  const kpis = design.kpis as Record<string, unknown>

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">KPIs y Métricas</h3>
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpis.expected_revenue && (
          <StatCard
            title="Ingresos Esperados"
            value={typeof kpis.expected_revenue === 'number' ? `$${kpis.expected_revenue.toLocaleString()}` : String(kpis.expected_revenue)}
            icon={<DollarSign className="w-5 h-5 text-green-600" />}
          />
        )}
        {kpis.target_customers && (
          <StatCard
            title="Clientes Objetivo"
            value={String(kpis.target_customers)}
            icon={<Users className="w-5 h-5 text-blue-600" />}
          />
        )}
        {kpis.break_even_point && (
          <StatCard
            title="Punto de Equilibrio"
            value={String(kpis.break_even_point)}
            icon={<TrendingUp className="w-5 h-5 text-purple-600" />}
          />
        )}
        {kpis.average_transaction && (
          <StatCard
            title="Transacción Promedio"
            value={typeof kpis.average_transaction === 'number' ? `$${kpis.average_transaction.toLocaleString()}` : String(kpis.average_transaction)}
            icon={<ShoppingCart className="w-5 h-5 text-orange-600" />}
          />
        )}
      </div>
    </div>
  )
}


