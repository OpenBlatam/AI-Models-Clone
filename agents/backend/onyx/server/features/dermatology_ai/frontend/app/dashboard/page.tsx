'use client';

import React, { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api/client';
import { DashboardOverview, UserAnalytics } from '@/lib/types/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { StatsCard } from '@/components/dashboard/StatsCard';
import { ProgressChart } from '@/components/dashboard/ProgressChart';
import { SkeletonCard } from '@/components/ui/Skeleton';
import { BarChart3, TrendingUp, AlertCircle, Clock, Activity, Target } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';
import toast from 'react-hot-toast';
import Link from 'next/link';
import { useAuth } from '@/lib/contexts/AuthContext';

export default function DashboardPage() {
  const { user } = useAuth();
  const [overview, setOverview] = useState<DashboardOverview | null>(null);
  const [analytics, setAnalytics] = useState<UserAnalytics | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (user) {
      loadDashboardData();
    }
  }, [user]);

  const loadDashboardData = async () => {
    if (!user) return;
    setIsLoading(true);
    try {
      const [overviewData, analyticsData] = await Promise.all([
        apiClient.getDashboardOverview(),
        apiClient.getUserAnalytics(user.id),
      ]);
      setOverview(overviewData);
      setAnalytics(analyticsData as any);
    } catch (error: any) {
      toast.error(error.message || 'Error al cargar el dashboard');
    } finally {
      setIsLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <Card className="p-8 text-center">
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Por favor inicia sesión para ver tu dashboard
          </p>
          <Link href="/">
            <Button>Ir al inicio</Button>
          </Link>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Dashboard
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Resumen de tu salud de la piel
          </p>
        </div>

        {/* Stats Grid */}
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {[1, 2, 3, 4].map((i) => (
              <SkeletonCard key={i} />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <StatsCard
              title="Total de Análisis"
              value={overview?.total_analyses || 0}
              icon={BarChart3}
              trend={{ value: 12, isPositive: true }}
              iconColor="text-primary-600 dark:text-primary-400"
            />
            <StatsCard
              title="Puntuación Promedio"
              value={overview?.average_score?.toFixed(1) || '0.0'}
              icon={TrendingUp}
              trend={{ value: 5, isPositive: true }}
              iconColor="text-green-600 dark:text-green-400"
            />
            <StatsCard
              title="Alertas Activas"
              value={overview?.active_alerts || 0}
              icon={AlertCircle}
              iconColor="text-yellow-600 dark:text-yellow-400"
            />
            <StatsCard
              title="Último Análisis"
              value={
                overview?.recent_analyses?.[0]?.timestamp
                  ? new Date(overview.recent_analyses[0].timestamp).toLocaleDateString('es-ES', {
                      day: 'numeric',
                      month: 'short',
                    })
                  : 'N/A'
              }
              icon={Clock}
              subtitle="Fecha del último análisis"
              iconColor="text-blue-600 dark:text-blue-400"
            />
          </div>
        )}

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {isLoading ? (
            <>
              <SkeletonCard />
              <SkeletonCard />
            </>
          ) : (
            <>
              {overview?.trends && overview.trends.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>Progreso en el Tiempo</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ProgressChart
                      data={overview.trends[0]?.values || []}
                      type="area"
                      color="#0ea5e9"
                    />
                  </CardContent>
                </Card>
              )}

              {analytics && analytics.average_scores && (
                <Card>
                  <CardHeader>
                    <CardTitle>Métricas de Calidad</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <RadarChart data={[
                        { metric: 'Textura', value: analytics.average_scores.texture_score },
                        { metric: 'Hidratación', value: analytics.average_scores.hydration_score },
                        { metric: 'Elasticidad', value: analytics.average_scores.elasticity_score },
                        { metric: 'Pigmentación', value: analytics.average_scores.pigmentation_score },
                        { metric: 'Poros', value: analytics.average_scores.pore_size_score },
                        { metric: 'Arrugas', value: analytics.average_scores.wrinkles_score },
                      ]}>
                        <PolarGrid />
                        <PolarAngleAxis dataKey="metric" />
                        <PolarRadiusAxis angle={90} domain={[0, 100]} />
                        <Radar
                          name="Puntuación"
                          dataKey="value"
                          stroke="#0ea5e9"
                          fill="#0ea5e9"
                          fillOpacity={0.6}
                        />
                        <Tooltip />
                      </RadarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              )}
            </>
          )}
        </div>

          {analytics && (
            <Card>
              <CardHeader>
                <CardTitle>Condiciones Más Comunes</CardTitle>
              </CardHeader>
              <CardContent>
                {analytics.most_common_conditions && analytics.most_common_conditions.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={analytics.most_common_conditions}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="condition" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="count" fill="#0ea5e9" />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <p className="text-gray-500 text-center py-8">
                    No hay datos de condiciones disponibles
                  </p>
                )}
              </CardContent>
            </Card>
          )}
        </div>

        {/* Recent Analyses */}
        {overview?.recent_analyses && overview.recent_analyses.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Análisis Recientes</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {overview.recent_analyses.slice(0, 5).map((analysis) => (
                  <div
                    key={analysis.record_id}
                    className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                  >
                    <div>
                      <p className="font-medium text-gray-900">
                        Análisis #{analysis.record_id.slice(0, 8)}
                      </p>
                      <p className="text-sm text-gray-600">
                        {new Date(analysis.timestamp).toLocaleString('es-ES')}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold text-primary-600">
                        {analysis.analysis.quality_scores.overall_score.toFixed(1)}
                      </p>
                      <p className="text-xs text-gray-500">Puntuación</p>
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-4 text-center">
                <Link
                  href="/history"
                  className="text-primary-600 hover:text-primary-700 font-medium"
                >
                  Ver todo el historial →
                </Link>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Quick Actions */}
        <Card className="mt-8">
          <CardHeader>
            <CardTitle>Acciones Rápidas</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Link
                href="/"
                className="p-4 bg-primary-50 rounded-lg hover:bg-primary-100 transition-colors text-center"
              >
                <p className="font-medium text-primary-900">Nuevo Análisis</p>
                <p className="text-sm text-primary-700 mt-1">
                  Analiza una nueva imagen
                </p>
              </Link>
              <Link
                href="/history"
                className="p-4 bg-secondary-50 rounded-lg hover:bg-secondary-100 transition-colors text-center"
              >
                <p className="font-medium text-secondary-900">Ver Historial</p>
                <p className="text-sm text-secondary-700 mt-1">
                  Revisa análisis anteriores
                </p>
              </Link>
              <Link
                href="/products"
                className="p-4 bg-green-50 rounded-lg hover:bg-green-100 transition-colors text-center"
              >
                <p className="font-medium text-green-900">Productos</p>
                <p className="text-sm text-green-700 mt-1">
                  Busca productos recomendados
                </p>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

