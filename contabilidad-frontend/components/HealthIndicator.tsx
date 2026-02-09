'use client';

import { memo, useMemo } from 'react';
import { useHealthCheck } from '@/lib';

function HealthIndicatorComponent() {
  const { isHealthy, isChecking, error, lastChecked } = useHealthCheck(30000);

  const statusColor = useMemo(() => {
    if (isChecking) return 'bg-yellow-500';
    if (isHealthy) return 'bg-green-500';
    return 'bg-red-500';
  }, [isChecking, isHealthy]);

  const statusText = useMemo(() => {
    if (isChecking) return 'Verificando...';
    if (isHealthy) return 'Conectado';
    return 'Desconectado';
  }, [isChecking, isHealthy]);

  return (
    <div className="flex items-center gap-2 text-sm">
      <div className={`w-2 h-2 rounded-full ${statusColor} animate-pulse`}></div>
      <span className="text-gray-600 dark:text-gray-400">{statusText}</span>
      {error && (
        <span className="text-red-500 text-xs" title={error.message}>
          ⚠️
        </span>
      )}
      {lastChecked && (
        <span className="text-gray-400 dark:text-gray-500 text-xs">
          ({lastChecked.toLocaleTimeString('es-MX')})
        </span>
      )}
    </div>
  );
}

export const HealthIndicator = memo(HealthIndicatorComponent);





