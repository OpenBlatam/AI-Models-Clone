'use client';

import { useState } from 'react';
import { TaskHistoryItem } from '@/lib/hooks/useTaskHistory';

interface AdvancedSearchProps {
  onSearch: (filters: SearchFilters) => void;
  onReset: () => void;
}

export interface SearchFilters {
  query: string;
  status?: TaskHistoryItem['status'];
  serviceType?: string;
  dateFrom?: string;
  dateTo?: string;
  favoritesOnly?: boolean;
}

export function AdvancedSearch({ onSearch, onReset }: AdvancedSearchProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [filters, setFilters] = useState<SearchFilters>({
    query: '',
    favoritesOnly: false,
  });

  const handleApply = () => {
    onSearch(filters);
    setIsOpen(false);
  };

  const handleReset = () => {
    setFilters({ query: '', favoritesOnly: false });
    onReset();
    setIsOpen(false);
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="px-3 py-1 text-sm bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 rounded-lg transition-colors"
      >
        🔍 Búsqueda Avanzada
      </button>

      {isOpen && (
        <div className="absolute top-full right-0 mt-2 w-80 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 p-4 z-50">
          <h3 className="font-bold text-gray-900 dark:text-white mb-4">
            Búsqueda Avanzada
          </h3>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Texto
              </label>
              <input
                type="text"
                value={filters.query}
                onChange={(e) => setFilters({ ...filters, query: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                placeholder="Buscar en tareas..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Estado
              </label>
              <select
                value={filters.status || ''}
                onChange={(e) =>
                  setFilters({
                    ...filters,
                    status: e.target.value as TaskHistoryItem['status'] | undefined,
                  })
                }
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="">Todos</option>
                <option value="completed">Completadas</option>
                <option value="running">En Proceso</option>
                <option value="pending">Pendientes</option>
                <option value="failed">Fallidas</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Tipo de Servicio
              </label>
              <select
                value={filters.serviceType || ''}
                onChange={(e) =>
                  setFilters({ ...filters, serviceType: e.target.value || undefined })
                }
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="">Todos</option>
                <option value="calcular_impuestos">Cálculo de Impuestos</option>
                <option value="asesoria_fiscal">Asesoría Fiscal</option>
                <option value="guia_fiscal">Guía Fiscal</option>
                <option value="tramite_sat">Trámite SAT</option>
                <option value="ayuda_declaracion">Ayuda con Declaración</option>
              </select>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="favoritesOnly"
                checked={filters.favoritesOnly}
                onChange={(e) =>
                  setFilters({ ...filters, favoritesOnly: e.target.checked })
                }
                className="rounded border-gray-300 dark:border-gray-600"
              />
              <label
                htmlFor="favoritesOnly"
                className="text-sm text-gray-700 dark:text-gray-300"
              >
                Solo favoritos
              </label>
            </div>

            <div className="flex gap-2 pt-2">
              <button
                onClick={handleApply}
                className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
              >
                Aplicar
              </button>
              <button
                onClick={handleReset}
                className="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                Limpiar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}














