'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { TrendingUp } from 'lucide-react'
import type { StoreDesign } from '@/types'

interface FinancialChartProps {
  design: StoreDesign
}

export function FinancialChart({ design }: FinancialChartProps) {
  if (!design.financial_analysis) return null

  const financial = design.financial_analysis as Record<string, unknown>

  const monthlyData = financial.monthly_projection
    ? Object.entries(financial.monthly_projection as Record<string, number>).map(
        ([month, revenue]) => ({
          month: month.substring(0, 3),
          revenue,
          expenses: (revenue * 0.6) | 0,
          profit: (revenue * 0.4) | 0,
        })
      )
    : []

  const budgetData = Object.entries(design.decoration_plan.budget_estimate).map(
    ([category, amount]) => ({
      category: category.substring(0, 15),
      amount,
    })
  )

  return (
    <div className="grid md:grid-cols-2 gap-4">
      {monthlyData.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5" />
              Proyección Mensual
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={monthlyData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="revenue"
                  stroke="#3b82f6"
                  name="Ingresos"
                />
                <Line
                  type="monotone"
                  dataKey="expenses"
                  stroke="#ef4444"
                  name="Gastos"
                />
                <Line
                  type="monotone"
                  dataKey="profit"
                  stroke="#10b981"
                  name="Ganancia"
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {budgetData.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Distribución de Presupuesto</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={budgetData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="category" angle={-45} textAnchor="end" height={80} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="amount" fill="#8b5cf6" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}
    </div>
  )
}


