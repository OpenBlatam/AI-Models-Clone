'use client';

import { useTaskHistory } from '@/lib/hooks/useTaskHistory';
import { formatDate } from '@/lib/utils/formatDate';
import { Badge } from './Badge';

export function CalendarView() {
  const { history } = useTaskHistory();

  // Agrupar tareas por fecha
  const tasksByDate = history.reduce((acc, task) => {
    const date = new Date(task.createdAt).toISOString().split('T')[0];
    if (!acc[date]) {
      acc[date] = [];
    }
    acc[date].push(task);
    return acc;
  }, {} as Record<string, typeof history>);

  const dates = Object.keys(tasksByDate).sort().reverse().slice(0, 30); // Últimos 30 días

  if (dates.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
          Vista de Calendario
        </h2>
        <p className="text-gray-500 dark:text-gray-400 text-center py-8">
          No hay tareas para mostrar
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
      <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
        Vista de Calendario
      </h2>
      <div className="space-y-4 max-h-96 overflow-y-auto">
        {dates.map((date) => (
          <div key={date} className="border-b border-gray-200 dark:border-gray-700 pb-4 last:border-0">
            <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              {formatDate(date)}
            </h3>
            <div className="space-y-2">
              {tasksByDate[date].map((task) => (
                <div
                  key={task.taskId}
                  className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-900 rounded"
                >
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      {task.title}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {task.serviceType.replace('_', ' ')}
                    </p>
                  </div>
                  <Badge
                    variant={
                      task.status === 'completed'
                        ? 'success'
                        : task.status === 'failed'
                        ? 'error'
                        : task.status === 'running'
                        ? 'info'
                        : 'default'
                    }
                    size="sm"
                  >
                    {task.status}
                  </Badge>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}














