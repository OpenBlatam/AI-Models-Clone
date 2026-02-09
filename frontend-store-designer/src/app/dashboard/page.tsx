'use client'

import { useDashboard } from '@/hooks/use-dashboard'
import { Skeleton } from '@/components/ui/skeleton'
import { StatCard } from '@/components/stat-card'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { TrendingUp, Store, MessageSquare, BarChart3 } from 'lucide-react'

export default function DashboardPage() {
  const { data: dashboard, isLoading } = useDashboard()

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Skeleton className="h-8 w-48 mb-6" />
        <div className="grid md:grid-cols-4 gap-4 mb-6">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-4 w-24" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-8 w-16" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  const stats = dashboard as Record<string, unknown> | undefined

  const chartData = stats?.designs_by_type
    ? Object.entries(stats.designs_by_type as Record<string, number>).map(
        ([name, value]) => ({ name, value })
      )
    : []

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Dashboard</h1>

      <div className="grid md:grid-cols-4 gap-4 mb-6">
        <StatCard
          title="Total Diseños"
          value={stats?.total_designs || 0}
          description="Diseños creados"
          icon={<Store className="w-4 h-4 text-blue-600" />}
        />
        <StatCard
          title="Sesiones de Chat"
          value={stats?.total_sessions || 0}
          description="Conversaciones"
          icon={<MessageSquare className="w-4 h-4 text-green-600" />}
        />
        <StatCard
          title="Análisis"
          value={stats?.total_analyses || 0}
          description="Análisis completados"
          icon={<BarChart3 className="w-4 h-4 text-purple-600" />}
        />
        <StatCard
          title="Tendencia"
          value={stats?.recent_activity || 0}
          description="Actividad reciente"
          icon={<TrendingUp className="w-4 h-4 text-orange-600" />}
        />
      </div>

      {chartData.length > 0 && (
        <div className="grid md:grid-cols-2 gap-6 mb-6">
          <div className="bg-white rounded-lg border p-6">
            <h3 className="text-lg font-semibold mb-4">Diseños por Tipo</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-white rounded-lg border p-6">
            <h3 className="text-lg font-semibold mb-4">Distribución</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={chartData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) =>
                    `${name} ${(percent * 100).toFixed(0)}%`
                  }
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {chartData.map((_, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={COLORS[index % COLORS.length]}
                    />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {stats && Object.keys(stats).length > 0 && (
        <div className="bg-white rounded-lg border p-6">
          <h3 className="text-lg font-semibold mb-4">Datos Completos</h3>
          <pre className="bg-gray-50 p-4 rounded-lg overflow-auto text-xs">
            {JSON.stringify(stats, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )
}

