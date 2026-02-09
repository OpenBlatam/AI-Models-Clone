'use client';

import { useState, useEffect, useMemo, useCallback, memo } from 'react';
import {
  useTaskPolling,
  useTaskHistory,
  getTaskTitle,
  getTaskStatusInfo,
  formatServiceType,
  formatDateTime,
  formatRelativeTime,
  ExportMenu,
} from '@/lib';
import { LoadingSpinner } from './LoadingSpinner';
import { CopyButton } from './CopyButton';
import { ResultViewer } from './ResultViewer';
import { ProgressBar } from './ProgressBar';
import { NotesPanel } from './NotesPanel';
import { ShareModal } from './ShareModal';
import { EmptyState } from './EmptyState';

interface TaskMonitorProps {
  taskId: string | null;
}

function TaskMonitorComponent({ taskId }: TaskMonitorProps) {
  const { status, result, isLoading, error } = useTaskPolling({
    taskId,
    enabled: !!taskId,
    interval: 2000,
  });
  const { addTask, updateTask, history } = useTaskHistory();
  const [showShareModal, setShowShareModal] = useState(false);
  const [showNotes, setShowNotes] = useState(false);

  const handleShareClick = useCallback(() => setShowShareModal(true), []);
  const handleShareClose = useCallback(() => setShowShareModal(false), []);
  const handleNotesToggle = useCallback(() => setShowNotes(prev => !prev), []);

  // Agregar/actualizar tarea en historial
  useEffect(() => {
    if (status) {
      const taskTitle = getTaskTitle(status);
      const taskData = {
        taskId: status.id,
        serviceType: status.service_type,
        status: status.status,
        createdAt: status.created_at,
        completedAt: status.completed_at,
        result: result || undefined,
        title: taskTitle,
      };

      const existingTask = history.find((t) => t.taskId === status.id);
      if (existingTask) {
        updateTask(status.id, taskData);
      } else {
        addTask(taskData);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [status?.id, status?.status, result, history, addTask, updateTask]);


  if (!taskId) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
          Monitor de Tareas
        </h2>
        <EmptyState
          icon="📊"
          title="Sin tareas activas"
          description="Crea una nueva tarea desde el dashboard para ver su progreso aquí en tiempo real."
        />
      </div>
    );
  }


  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
      <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
        Monitor de Tareas
      </h2>

      {error && (
        <div className="mb-4 p-4 bg-red-100 dark:bg-red-900/20 border border-red-400 dark:border-red-600 rounded-lg">
          <p className="text-red-700 dark:text-red-400 text-sm">
            Error: {error.message}
          </p>
        </div>
      )}

      {status && (() => {
        const statusInfo = getTaskStatusInfo(status.status);
        return (
          <div className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Estado
                </span>
                <div className="flex items-center gap-2">
                  {isLoading && status.status !== 'completed' && (
                    <LoadingSpinner size="sm" />
                  )}
                  <span
                    className={`px-3 py-1 rounded-full text-white text-xs font-semibold ${statusInfo.bgColor}`}
                  >
                    {statusInfo.icon} {statusInfo.label}
                  </span>
                </div>
              </div>
              {isLoading && status.status !== 'completed' && (
                <div className="mt-2">
                  <ProgressBar
                    progress={status.status === 'running' ? 50 : 25}
                    showPercentage={false}
                    color={statusInfo.color}
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Verificando estado...</p>
                </div>
              )}
            </div>

            <div className="text-sm space-y-2">
              <div>
                <span className="font-medium text-gray-700 dark:text-gray-300">ID de Tarea:</span>
                <p className="text-gray-500 dark:text-gray-400 font-mono text-xs break-all">
                  {status.id}
                </p>
              </div>
              <div>
                <span className="font-medium text-gray-700 dark:text-gray-300">Tipo:</span>
                <p className="text-gray-500 dark:text-gray-400 capitalize">
                  {formatServiceType(status.service_type)}
                </p>
              </div>
            {status.created_at && (
              <div>
                <span className="font-medium text-gray-700 dark:text-gray-300">Creada:</span>
                <p className="text-gray-500 dark:text-gray-400" title={formatDateTime(status.created_at)}>
                  {formatRelativeTime(status.created_at)}
                </p>
              </div>
            )}
            {status.completed_at && (
              <div>
                <span className="font-medium text-gray-700 dark:text-gray-300">Completada:</span>
                <p className="text-gray-500 dark:text-gray-400" title={formatDateTime(status.completed_at)}>
                  {formatRelativeTime(status.completed_at)}
                </p>
              </div>
            )}
            </div>
          </div>
        );
      })()}

      {result && (
        <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
          <div className="flex justify-between items-center mb-3 flex-wrap gap-2">
            <h3 className="text-lg font-bold text-gray-900 dark:text-white">
              Resultado
            </h3>
            <div className="flex gap-2 flex-wrap">
              <CopyButton text={result.resultado} />
              <button
                onClick={handleShareClick}
                className="px-3 py-1 text-sm bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 rounded-lg transition-colors"
              >
                🔗 Compartir
              </button>
              <button
                onClick={handleNotesToggle}
                className="px-3 py-1 text-sm bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 rounded-lg transition-colors"
              >
                📝 {showNotes ? 'Ocultar' : 'Mostrar'} Notas
              </button>
              {status && result && <ExportMenu status={status} result={result} />}
            </div>
          </div>
          <ResultViewer result={result} />
          
          {showNotes && status && (
            <div className="mt-4">
              <NotesPanel taskId={status.id} />
            </div>
          )}
        </div>
      )}

      {status && result && (
        <ShareModal
          isOpen={showShareModal}
          onClose={handleShareClose}
          task={{ status, result }}
        />
      )}
    </div>
  );
}

export const TaskMonitor = memo(TaskMonitorComponent);

