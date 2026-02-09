'use client';

interface StatusIndicatorProps {
  status: 'online' | 'offline' | 'connecting' | 'error';
  size?: 'sm' | 'md' | 'lg';
}

export function StatusIndicator({ status, size = 'md' }: StatusIndicatorProps) {
  const sizeClasses = {
    sm: 'w-2 h-2',
    md: 'w-3 h-3',
    lg: 'w-4 h-4',
  };

  const statusClasses = {
    online: 'bg-green-500',
    offline: 'bg-gray-400',
    connecting: 'bg-yellow-500 animate-pulse',
    error: 'bg-red-500',
  };

  const statusLabels = {
    online: 'En línea',
    offline: 'Sin conexión',
    connecting: 'Conectando...',
    error: 'Error de conexión',
  };

  return (
    <div className="flex items-center gap-2" title={statusLabels[status]}>
      <div
        className={`${sizeClasses[size]} ${statusClasses[status]} rounded-full`}
        aria-label={statusLabels[status]}
      ></div>
      <span className="text-xs text-gray-600 dark:text-gray-400">
        {statusLabels[status]}
      </span>
    </div>
  );
}














