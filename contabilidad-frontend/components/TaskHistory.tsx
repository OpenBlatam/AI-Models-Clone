'use client';

import { useState, useMemo } from 'react';
import { useTaskHistory, useFavorites, formatRelativeTime } from '@/lib';
import type { TaskHistoryItem } from '@/lib';
import { SearchBar } from './SearchBar';
import { FilterBar } from './FilterBar';
import { AdvancedSearch } from './AdvancedSearch';
import { ConfirmDialog } from './ConfirmDialog';
import { CompactView } from './CompactView';

interface TaskHistoryProps {
  onSelectTask: (taskId: string) => void;
  selectedTaskId?: string | null;
}

type FilterStatus = 'all' | TaskHistoryItem['status'];

export function TaskHistory({ onSelectTask, selectedTaskId }: TaskHistoryProps) {
  const { history, removeTask, clearHistory } = useTaskHistory();
  const { toggleFavorite, isFavorite } = useFavorites();
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState<FilterStatus>('all');
  const [showClearConfirm, setShowClearConfirm] = useState(false);
  const [showFavoritesOnly, setShowFavoritesOnly] = useState(false);

  const filteredHistory = useMemo(() => {
    return history.filter((task) => {
      const matchesSearch =
        searchQuery === '' ||
        task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        task.serviceType.toLowerCase().includes(searchQuery.toLowerCase()) ||
        task.taskId.toLowerCase().includes(searchQuery.toLowerCase());

      const matchesFilter = filterStatus === 'all' || task.status === filterStatus;
      
      const matchesFavorites = !showFavoritesOnly || isFavorite(task.taskId);

      return matchesSearch && matchesFilter && matchesFavorites;
    });
  }, [history, searchQuery, filterStatus, showFavoritesOnly, isFavorite]);

  const getStatusColor = useCallback((status: TaskHistoryItem['status']) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'running':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      case 'failed':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      default:
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
    }
  }, []);

  const getStatusText = useCallback((status: TaskHistoryItem['status']) => {
    switch (status) {
      case 'completed':
        return 'Completada';
      case 'running':
        return 'En Proceso';
      case 'failed':
        return 'Fallida';
      default:
        return 'Pendiente';
    }
  }, []);

  if (history.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">
            Historial de Tareas
          </h2>
        </div>
        <p className="text-gray-500 dark:text-gray-400 text-sm text-center py-8">
          No hay tareas en el historial
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white">
          Historial de Tareas ({filteredHistory.length}/{history.length})
        </h2>
        <button
          onClick={() => setShowClearConfirm(true)}
          className="text-sm text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300"
        >
          Limpiar
        </button>
      </div>

      <ConfirmDialog
        isOpen={showClearConfirm}
        title="Limpiar Historial"
        message="¿Estás seguro de que deseas eliminar todo el historial de tareas? Esta acción no se puede deshacer."
        confirmText="Limpiar Todo"
        cancelText="Cancelar"
        variant="danger"
        onConfirm={() => {
          clearHistory();
          setShowClearConfirm(false);
        }}
        onCancel={() => setShowClearConfirm(false)}
      />
      
      <div className="mb-4 space-y-3">
        <div className="flex gap-2">
          <div className="flex-1">
            <SearchBar
              onSearch={setSearchQuery}
              placeholder="Buscar por título, tipo o ID..."
            />
          </div>
          <AdvancedSearch
            onSearch={(filters) => {
              setSearchQuery(filters.query);
              setFilterStatus(filters.status || 'all');
              setShowFavoritesOnly(filters.favoritesOnly || false);
            }}
            onReset={() => {
              setSearchQuery('');
              setFilterStatus('all');
              setShowFavoritesOnly(false);
            }}
          />
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <FilterBar
            onFilterChange={setFilterStatus}
            activeFilter={filterStatus}
          />
          <button
            onClick={() => setShowFavoritesOnly(!showFavoritesOnly)}
            className={`px-3 py-1 rounded-full text-sm font-medium transition-all ${
              showFavoritesOnly
                ? 'bg-yellow-500 text-white shadow-md'
                : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
            }`}
          >
            ⭐ Favoritos
          </button>
        </div>
      </div>

      {filteredHistory.length === 0 ? (
        <EmptyState
          icon="🔍"
          title="No se encontraron tareas"
          description={
            searchQuery || filterStatus !== 'all' || showFavoritesOnly
              ? "No hay tareas que coincidan con tu búsqueda o filtros. Intenta con otros criterios."
              : "Aún no has creado ninguna tarea. Selecciona un servicio para comenzar."
          }
        />
      ) : (
        <CompactView>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {filteredHistory.map((task) => (
              <div
                key={task.taskId}
                onClick={() => onSelectTask(task.taskId)}
                className={`p-3 rounded-lg border cursor-pointer transition-all ${
                  selectedTaskId === task.taskId
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                    : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                }`}
              >
                <div className="flex justify-between items-start mb-2">
                  <div className="flex-1 flex items-start gap-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleFavorite(task.taskId);
                      }}
                      className={`text-lg transition-transform hover:scale-110 ${
                        isFavorite(task.taskId)
                          ? 'text-yellow-500'
                          : 'text-gray-300 dark:text-gray-600 hover:text-yellow-400'
                      }`}
                      aria-label={isFavorite(task.taskId) ? 'Quitar de favoritos' : 'Agregar a favoritos'}
                    >
                      {isFavorite(task.taskId) ? '⭐' : '☆'}
                    </button>
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900 dark:text-white text-sm">
                        {task.title}
                      </h3>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        {task.serviceType.replace('_', ' ')}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      removeTask(task.taskId);
                    }}
                    className="text-gray-400 hover:text-red-500 dark:hover:text-red-400 ml-2"
                    aria-label="Eliminar tarea"
                  >
                    ×
                  </button>
                </div>
            <div className="flex items-center justify-between mt-2">
              <span
                className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(
                  task.status
                )}`}
              >
                {getStatusText(task.status)}
              </span>
              <span className="text-xs text-gray-400 dark:text-gray-500">
                {formatRelativeTime(new Date(task.createdAt))}
              </span>
            </div>
          </div>
        ))}
        </div>
      )}
    </div>
  );
}

