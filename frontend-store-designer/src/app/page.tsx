'use client'

import Link from 'next/link'
import { useDashboard } from '@/hooks/use-dashboard'
import { Store, MessageSquare, BarChart3, Sparkles, TrendingUp, Zap } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'

export default function Home() {
  const { data: dashboard, isLoading } = useDashboard()

  const stats = dashboard as Record<string, unknown> | undefined

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Physical Store Designer AI
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-6">
            Diseña locales físicos completos con IA. Genera diseños, planes de
            marketing y estrategias de decoración en minutos.
          </p>
          {isLoading ? (
            <div className="flex justify-center gap-4">
              <Skeleton className="h-8 w-24" />
              <Skeleton className="h-8 w-24" />
              <Skeleton className="h-8 w-24" />
            </div>
          ) : (
            <div className="flex justify-center gap-6 text-sm">
              <div className="flex items-center gap-2">
                <Store className="w-5 h-5 text-blue-600" />
                <span className="font-semibold">{stats?.total_designs || 0}</span>
                <span className="text-gray-600">Diseños</span>
              </div>
              <div className="flex items-center gap-2">
                <MessageSquare className="w-5 h-5 text-green-600" />
                <span className="font-semibold">{stats?.total_sessions || 0}</span>
                <span className="text-gray-600">Chats</span>
              </div>
              <div className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-purple-600" />
                <span className="font-semibold">{stats?.recent_activity || 0}</span>
                <span className="text-gray-600">Activos</span>
              </div>
            </div>
          )}
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto mb-12">
          <Link
            href="/chat"
            className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-all hover:scale-105 group"
          >
            <MessageSquare className="w-12 h-12 text-blue-600 mb-4 group-hover:scale-110 transition-transform" />
            <h2 className="text-xl font-semibold mb-2">Chat Interactivo</h2>
            <p className="text-gray-600 text-sm">
              Conversa con la IA para definir tu local ideal paso a paso
            </p>
          </Link>

          <Link
            href="/design"
            className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-all hover:scale-105 group"
          >
            <Store className="w-12 h-12 text-green-600 mb-4 group-hover:scale-110 transition-transform" />
            <h2 className="text-xl font-semibold mb-2">Crear Diseño</h2>
            <p className="text-gray-600 text-sm">
              Genera un diseño completo con formulario rápido
            </p>
          </Link>

          <Link
            href="/designs"
            className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-all hover:scale-105 group"
          >
            <Sparkles className="w-12 h-12 text-purple-600 mb-4 group-hover:scale-110 transition-transform" />
            <h2 className="text-xl font-semibold mb-2">Mis Diseños</h2>
            <p className="text-gray-600 text-sm">
              Revisa, edita y gestiona todos tus diseños creados
            </p>
          </Link>

          <Link
            href="/dashboard"
            className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-all hover:scale-105 group"
          >
            <BarChart3 className="w-12 h-12 text-orange-600 mb-4 group-hover:scale-110 transition-transform" />
            <h2 className="text-xl font-semibold mb-2">Dashboard</h2>
            <p className="text-gray-600 text-sm">
              Analiza métricas, tendencias y estadísticas detalladas
            </p>
          </Link>
        </div>

        <div className="max-w-6xl mx-auto">
          <FeatureHighlights />
        </div>
      </div>
    </div>
  )
}
