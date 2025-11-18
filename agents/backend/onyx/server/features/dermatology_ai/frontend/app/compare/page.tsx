'use client';

import React, { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';
import { HistoryRecord, ComparisonResponse } from '@/lib/types/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Loading } from '@/components/ui/Loading';
import { Compare, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import toast from 'react-hot-toast';
import { useAuth } from '@/lib/contexts/AuthContext';

export default function ComparePage() {
  const { user } = useAuth();
  const [records, setRecords] = useState<HistoryRecord[]>([]);
  const [selectedRecord1, setSelectedRecord1] = useState<string | null>(null);
  const [selectedRecord2, setSelectedRecord2] = useState<string | null>(null);
  const [comparison, setComparison] = useState<ComparisonResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingComparison, setIsLoadingComparison] = useState(false);

  useEffect(() => {
    if (user) {
      loadRecords();
    }
  }, [user]);

  const loadRecords = async () => {
    if (!user) return;
    setIsLoading(true);
    try {
      const response = await apiClient.getHistory(user.id);
      setRecords(response.records || []);
    } catch (error: any) {
      toast.error(error.message || 'Error al cargar el historial');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCompare = async () => {
    if (!selectedRecord1 || !selectedRecord2) {
      toast.error('Por favor selecciona dos análisis para comparar');
      return;
    }

    if (selectedRecord1 === selectedRecord2) {
      toast.error('Por favor selecciona dos análisis diferentes');
      return;
    }

    setIsLoadingComparison(true);
    try {
      const result = await apiClient.compareHistory(selectedRecord1, selectedRecord2);
      setComparison(result);
      toast.success('Comparación completada');
    } catch (error: any) {
      toast.error(error.message || 'Error al comparar análisis');
    } finally {
      setIsLoadingComparison(false);
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="p-8 text-center">
          <p className="text-gray-600 mb-4">
            Por favor inicia sesión para comparar análisis
          </p>
          <Button href="/">Ir al inicio</Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <div className="flex items-center space-x-3 mb-2">
            <Compare className="h-8 w-8 text-primary-600" />
            <h1 className="text-3xl font-bold text-gray-900">Comparar Análisis</h1>
          </div>
          <p className="text-gray-600">
            Compara dos análisis para ver tu progreso
          </p>
        </div>

        {isLoading ? (
          <Loading fullScreen text="Cargando historial..." />
        ) : (
          <div className="space-y-6">
            {/* Selection */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Análisis 1</CardTitle>
                </CardHeader>
                <CardContent>
                  <select
                    value={selectedRecord1 || ''}
                    onChange={(e) => setSelectedRecord1(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="">Selecciona un análisis</option>
                    {records.map((record) => (
                      <option key={record.record_id} value={record.record_id}>
                        {new Date(record.timestamp).toLocaleDateString()} - Score:{' '}
                        {record.analysis.quality_scores.overall_score.toFixed(1)}
                      </option>
                    ))}
                  </select>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Análisis 2</CardTitle>
                </CardHeader>
                <CardContent>
                  <select
                    value={selectedRecord2 || ''}
                    onChange={(e) => setSelectedRecord2(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="">Selecciona un análisis</option>
                    {records.map((record) => (
                      <option key={record.record_id} value={record.record_id}>
                        {new Date(record.timestamp).toLocaleDateString()} - Score:{' '}
                        {record.analysis.quality_scores.overall_score.toFixed(1)}
                      </option>
                    ))}
                  </select>
                </CardContent>
              </Card>
            </div>

            <div className="text-center">
              <Button
                onClick={handleCompare}
                isLoading={isLoadingComparison}
                disabled={!selectedRecord1 || !selectedRecord2}
                size="lg"
              >
                Comparar Análisis
              </Button>
            </div>

            {/* Comparison Results */}
            {comparison && (
              <div className="space-y-6 animate-fade-in">
                <Card>
                  <CardHeader>
                    <CardTitle>Resumen de Comparación</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="text-center p-4 bg-gray-50 rounded-lg">
                        <p className="text-sm text-gray-600 mb-1">Análisis 1</p>
                        <p className="text-2xl font-bold text-primary-600">
                          {comparison.comparison.record1.analysis.quality_scores.overall_score.toFixed(1)}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          {new Date(comparison.comparison.record1.timestamp).toLocaleDateString()}
                        </p>
                      </div>

                      <div className="text-center p-4 bg-gray-50 rounded-lg">
                        <p className="text-sm text-gray-600 mb-1">Mejora General</p>
                        <div className="flex items-center justify-center">
                          {comparison.comparison.overall_improvement > 0 ? (
                            <TrendingUp className="h-6 w-6 text-green-600 mr-2" />
                          ) : comparison.comparison.overall_improvement < 0 ? (
                            <TrendingDown className="h-6 w-6 text-red-600 mr-2" />
                          ) : (
                            <Minus className="h-6 w-6 text-gray-600 mr-2" />
                          )}
                          <p
                            className={`text-2xl font-bold ${
                              comparison.comparison.overall_improvement > 0
                                ? 'text-green-600'
                                : comparison.comparison.overall_improvement < 0
                                ? 'text-red-600'
                                : 'text-gray-600'
                            }`}
                          >
                            {comparison.comparison.overall_improvement > 0 ? '+' : ''}
                            {comparison.comparison.overall_improvement.toFixed(1)}
                          </p>
                        </div>
                      </div>

                      <div className="text-center p-4 bg-gray-50 rounded-lg">
                        <p className="text-sm text-gray-600 mb-1">Análisis 2</p>
                        <p className="text-2xl font-bold text-primary-600">
                          {comparison.comparison.record2.analysis.quality_scores.overall_score.toFixed(1)}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          {new Date(comparison.comparison.record2.timestamp).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Cambios por Métrica</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {comparison.comparison.differences.map((diff, index) => (
                        <div
                          key={index}
                          className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                        >
                          <span className="font-medium text-gray-900 capitalize">
                            {diff.metric.replace('_', ' ')}
                          </span>
                          <div className="flex items-center space-x-4">
                            <div className="flex items-center">
                              {diff.change > 0 ? (
                                <TrendingUp className="h-4 w-4 text-green-600 mr-1" />
                              ) : diff.change < 0 ? (
                                <TrendingDown className="h-4 w-4 text-red-600 mr-1" />
                              ) : (
                                <Minus className="h-4 w-4 text-gray-600 mr-1" />
                              )}
                              <span
                                className={`font-semibold ${
                                  diff.change > 0
                                    ? 'text-green-600'
                                    : diff.change < 0
                                    ? 'text-red-600'
                                    : 'text-gray-600'
                                }`}
                              >
                                {diff.change > 0 ? '+' : ''}
                                {diff.change.toFixed(1)} ({diff.percentage > 0 ? '+' : ''}
                                {diff.percentage.toFixed(1)}%)
                              </span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

