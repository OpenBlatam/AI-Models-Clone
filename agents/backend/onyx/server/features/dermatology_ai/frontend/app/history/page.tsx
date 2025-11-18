'use client';

import React, { useEffect, useState, useMemo } from 'react';
import { apiClient } from '@/lib/api/client';
import { HistoryRecord } from '@/lib/types/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { SearchBar } from '@/components/ui/SearchBar';
import { FilterBar, FilterOption } from '@/components/ui/FilterBar';
import { History, Calendar, TrendingUp, TrendingDown } from 'lucide-react';
import toast from 'react-hot-toast';
import { format } from 'date-fns';
import { useAuth } from '@/lib/contexts/AuthContext';

export default function HistoryPage() {
  const [records, setRecords] = useState<HistoryRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedRecord, setSelectedRecord] = useState<HistoryRecord | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [skinTypeFilter, setSkinTypeFilter] = useState('');
  const [dateFilter, setDateFilter] = useState('');
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      loadHistory();
    }
  }, [user]);

  const loadHistory = async () => {
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

  const filteredRecords = useMemo(() => {
    return records.filter((record) => {
      const matchesSearch =
        !searchQuery ||
        record.analysis.skin_type.toLowerCase().includes(searchQuery.toLowerCase()) ||
        record.notes?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        record.analysis.conditions?.some((c) =>
          c.name.toLowerCase().includes(searchQuery.toLowerCase())
        );

      const matchesSkinType =
        !skinTypeFilter || record.analysis.skin_type === skinTypeFilter;

      const matchesDate = !dateFilter || (() => {
        const recordDate = new Date(record.timestamp);
        const now = new Date();
        switch (dateFilter) {
          case 'today':
            return recordDate.toDateString() === now.toDateString();
          case 'week':
            const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
            return recordDate >= weekAgo;
          case 'month':
            const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
            return recordDate >= monthAgo;
          default:
            return true;
        }
      })();

      return matchesSearch && matchesSkinType && matchesDate;
    });
  }, [records, searchQuery, skinTypeFilter, dateFilter]);

  const skinTypeOptions: FilterOption[] = [
    { label: 'Seco', value: 'dry' },
    { label: 'Graso', value: 'oily' },
    { label: 'Mixto', value: 'combination' },
    { label: 'Normal', value: 'normal' },
    { label: 'Sensible', value: 'sensitive' },
  ];

  const dateOptions: FilterOption[] = [
    { label: 'Hoy', value: 'today' },
    { label: 'Esta semana', value: 'week' },
    { label: 'Este mes', value: 'month' },
  ];

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 80) return 'bg-green-100';
    if (score >= 60) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Cargando historial...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <div className="flex items-center space-x-3 mb-2">
            <History className="h-8 w-8 text-primary-600 dark:text-primary-400" />
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Historial de Análisis
            </h1>
          </div>
          <p className="text-gray-600 dark:text-gray-400">
            Revisa todos tus análisis anteriores y compara resultados
          </p>
        </div>

        {/* Search and Filters */}
        <div className="mb-6 space-y-4">
          <SearchBar
            placeholder="Buscar por tipo de piel, condiciones, notas..."
            onSearch={setSearchQuery}
            className="w-full"
          />
          <FilterBar
            filters={[
              {
                label: 'Tipo de Piel',
                options: skinTypeOptions,
                value: skinTypeFilter,
                onChange: setSkinTypeFilter,
              },
              {
                label: 'Fecha',
                options: dateOptions,
                value: dateFilter,
                onChange: setDateFilter,
              },
            ]}
            onClearAll={() => {
              setSkinTypeFilter('');
              setDateFilter('');
              setSearchQuery('');
            }}
          />
        </div>

        {filteredRecords.length === 0 ? (
          <Card className="p-12 text-center">
            <History className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-700 mb-2">
              No hay análisis en el historial
            </h3>
            <p className="text-gray-500 mb-6">
              Comienza analizando una imagen para ver tu historial aquí
            </p>
            <Button href="/">Realizar Primer Análisis</Button>
          </Card>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Records List */}
            <div className="lg:col-span-2 space-y-4">
              {filteredRecords.length > 0 && (
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  Mostrando {filteredRecords.length} de {records.length} análisis
                </p>
              )}
              {filteredRecords.map((record) => (
                <Card
                  key={record.record_id}
                  className={`cursor-pointer transition-all ${
                    selectedRecord?.record_id === record.record_id
                      ? 'ring-2 ring-primary-500'
                      : 'hover:shadow-lg'
                  }`}
                  onClick={() => setSelectedRecord(record)}
                >
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <Calendar className="h-4 w-4 text-gray-400" />
                          <span className="text-sm text-gray-600">
                            {format(
                              new Date(record.timestamp),
                              "d 'de' MMMM, yyyy 'a las' HH:mm"
                            )}
                          </span>
                        </div>
                        <div className="mb-3">
                          <span className="text-xs font-medium text-gray-500 uppercase">
                            Tipo de Piel
                          </span>
                          <p className="text-lg font-semibold text-gray-900 capitalize">
                            {record.analysis.skin_type}
                          </p>
                        </div>
                        {record.analysis.conditions && record.analysis.conditions.length > 0 && (
                          <div className="mb-3">
                            <span className="text-xs font-medium text-gray-500 uppercase">
                              Condiciones Detectadas
                            </span>
                            <div className="flex flex-wrap gap-2 mt-1">
                              {record.analysis.conditions.slice(0, 3).map((condition, idx) => (
                                <span
                                  key={idx}
                                  className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded"
                                >
                                  {condition.name}
                                </span>
                              ))}
                              {record.analysis.conditions.length > 3 && (
                                <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                                  +{record.analysis.conditions.length - 3} más
                                </span>
                              )}
                            </div>
                          </div>
                        )}
                        {record.notes && (
                          <p className="text-sm text-gray-600 mt-2 italic">
                            "{record.notes}"
                          </p>
                        )}
                      </div>
                      <div className="ml-4 text-right">
                        <div
                          className={`inline-flex items-center justify-center w-20 h-20 rounded-full text-2xl font-bold ${getScoreColor(
                            record.analysis.quality_scores.overall_score
                          )} ${getScoreBgColor(
                            record.analysis.quality_scores.overall_score
                          )}`}
                        >
                          {record.analysis.quality_scores.overall_score.toFixed(0)}
                        </div>
                        <p className="text-xs text-gray-500 mt-2">Puntuación</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Record Details */}
            <div className="lg:col-span-1">
              {selectedRecord ? (
                <Card className="sticky top-8">
                  <CardHeader>
                    <CardTitle>Detalles del Análisis</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <p className="text-sm text-gray-600 mb-1">Fecha</p>
                      <p className="font-medium">
                        {format(
                          new Date(selectedRecord.timestamp),
                          "d 'de' MMMM, yyyy"
                        )}
                      </p>
                    </div>

                    <div>
                      <p className="text-sm text-gray-600 mb-2">Métricas de Calidad</p>
                      <div className="space-y-2">
                        {Object.entries(selectedRecord.analysis.quality_scores)
                          .filter(([key]) => key !== 'overall_score')
                          .map(([key, value]) => (
                            <div key={key} className="flex items-center justify-between">
                              <span className="text-sm text-gray-700 capitalize">
                                {key.replace('_score', '').replace('_', ' ')}
                              </span>
                              <div className="flex items-center space-x-2">
                                <div className="w-24 bg-gray-200 rounded-full h-2">
                                  <div
                                    className={`h-2 rounded-full ${
                                      value >= 80
                                        ? 'bg-green-500'
                                        : value >= 60
                                        ? 'bg-yellow-500'
                                        : 'bg-red-500'
                                    }`}
                                    style={{ width: `${value}%` }}
                                  />
                                </div>
                                <span className="text-sm font-medium w-12 text-right">
                                  {value.toFixed(1)}
                                </span>
                              </div>
                            </div>
                          ))}
                      </div>
                    </div>

                    {selectedRecord.analysis.conditions &&
                      selectedRecord.analysis.conditions.length > 0 && (
                        <div>
                          <p className="text-sm text-gray-600 mb-2">Condiciones</p>
                          <div className="space-y-2">
                            {selectedRecord.analysis.conditions.map((condition, idx) => (
                              <div
                                key={idx}
                                className="p-2 bg-gray-50 rounded text-sm"
                              >
                                <div className="flex items-center justify-between mb-1">
                                  <span className="font-medium capitalize">
                                    {condition.name}
                                  </span>
                                  <span className="text-xs text-gray-500">
                                    {(condition.confidence * 100).toFixed(0)}%
                                  </span>
                                </div>
                                <span
                                  className={`text-xs px-2 py-1 rounded ${
                                    condition.severity === 'severe'
                                      ? 'bg-red-100 text-red-800'
                                      : condition.severity === 'moderate'
                                      ? 'bg-yellow-100 text-yellow-800'
                                      : 'bg-blue-100 text-blue-800'
                                  }`}
                                >
                                  {condition.severity}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                    <div className="pt-4 border-t">
                      <Button
                        variant="outline"
                        className="w-full"
                        onClick={() => {
                          // TODO: Implement comparison
                          toast.success('Función de comparación próximamente');
                        }}
                      >
                        Comparar con Otro
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ) : (
                <Card className="p-8 text-center text-gray-500">
                  <p>Selecciona un análisis para ver los detalles</p>
                </Card>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

