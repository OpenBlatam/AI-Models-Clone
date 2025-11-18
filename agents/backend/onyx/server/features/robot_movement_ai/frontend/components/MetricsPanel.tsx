'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api/client';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { RefreshCw } from 'lucide-react';

export default function MetricsPanel() {
  const [metrics, setMetrics] = useState<any>(null);
  const [cpuUsage, setCpuUsage] = useState<any>(null);
  const [memoryUsage, setMemoryUsage] = useState<any>(null);
  const [performance, setPerformance] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadMetrics();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadMetrics = async () => {
    setIsLoading(true);
    try {
      const [metricsData, cpu, memory, perf] = await Promise.all([
        apiClient.getMetrics(),
        apiClient.getCPUUsage(),
        apiClient.getMemoryUsage(),
        apiClient.getPerformanceMetrics(),
      ]);
      setMetrics(metricsData);
      setCpuUsage(cpu);
      setMemoryUsage(memory);
      setPerformance(perf);
    } catch (error) {
      console.error('Failed to load metrics:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Transform data for charts
  const transformMetricsForChart = (data: any) => {
    if (!data || typeof data !== 'object') return [];
    return Object.entries(data).map(([key, value]: [string, any]) => ({
      name: key,
      value: typeof value === 'object' && value.value ? value.value : value,
      timestamp: typeof value === 'object' && value.timestamp ? value.timestamp : new Date().toISOString(),
    }));
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-semibold text-white">Métricas del Sistema</h2>
          <button
            onClick={loadMetrics}
            disabled={isLoading}
            className="flex items-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-5 h-5 ${isLoading ? 'animate-spin' : ''}`} />
            Actualizar
          </button>
        </div>
      </div>

      {/* CPU Usage */}
      {cpuUsage && (
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-medium text-white mb-4">Uso de CPU</h3>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={transformMetricsForChart(cpuUsage)}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="name" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip
                contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }}
              />
              <Area
                type="monotone"
                dataKey="value"
                stroke="#0EA5E9"
                fill="#0EA5E9"
                fillOpacity={0.3}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Memory Usage */}
      {memoryUsage && (
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-medium text-white mb-4">Uso de Memoria</h3>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={transformMetricsForChart(memoryUsage)}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="name" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip
                contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }}
              />
              <Area
                type="monotone"
                dataKey="value"
                stroke="#10B981"
                fill="#10B981"
                fillOpacity={0.3}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Performance Metrics */}
      {performance && (
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-medium text-white mb-4">Métricas de Rendimiento</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={transformMetricsForChart(performance)}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="name" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip
                contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="value"
                stroke="#F59E0B"
                strokeWidth={2}
                dot={{ fill: '#F59E0B' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Raw Metrics */}
      {metrics && (
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-medium text-white mb-4">Todas las Métricas</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {Object.entries(metrics).map(([key, value]: [string, any]) => (
              <div key={key} className="p-4 bg-gray-700/50 rounded-lg">
                <p className="text-gray-400 text-sm mb-1">{key}</p>
                <p className="text-white font-medium">
                  {typeof value === 'object' && value.value
                    ? `${value.value}${value.unit || ''}`
                    : String(value)}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {!metrics && !cpuUsage && !memoryUsage && !performance && !isLoading && (
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-gray-700 text-center text-gray-400">
          No hay métricas disponibles
        </div>
      )}
    </div>
  );
}

