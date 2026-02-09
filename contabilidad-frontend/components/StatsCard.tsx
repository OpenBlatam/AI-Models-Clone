'use client';

import { useTaskHistory } from '@/lib/hooks/useTaskHistory';
import { AnimatedCounter } from './AnimatedCounter';
import { Card } from './Card';

export function StatsCard() {
  const { history } = useTaskHistory();

  const stats = {
    total: history.length,
    completed: history.filter((t) => t.status === 'completed').length,
    running: history.filter((t) => t.status === 'running').length,
    failed: history.filter((t) => t.status === 'failed').length,
  };

  const successRate =
    stats.total > 0 ? ((stats.completed / stats.total) * 100) : 0;

  if (stats.total === 0) {
    return null;
  }

  return (
    <Card title="Estadísticas">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="text-center">
          <div className="text-2xl font-bold text-gray-900 dark:text-white">
            <AnimatedCounter value={stats.total} />
          </div>
          <div className="text-sm text-gray-500 dark:text-gray-400">Total</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-green-600 dark:text-green-400">
            <AnimatedCounter value={stats.completed} />
          </div>
          <div className="text-sm text-gray-500 dark:text-gray-400">Completadas</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
            <AnimatedCounter value={stats.running} />
          </div>
          <div className="text-sm text-gray-500 dark:text-gray-400">En Proceso</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-red-600 dark:text-red-400">
            <AnimatedCounter value={stats.failed} />
          </div>
          <div className="text-sm text-gray-500 dark:text-gray-400">Fallidas</div>
        </div>
      </div>
      <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
        <div className="text-center">
          <div className="text-lg font-semibold text-gray-900 dark:text-white">
            <AnimatedCounter value={successRate} decimals={1} suffix="%" />
          </div>
          <div className="text-sm text-gray-500 dark:text-gray-400">Tasa de Éxito</div>
        </div>
      </div>
    </Card>
  );
}

