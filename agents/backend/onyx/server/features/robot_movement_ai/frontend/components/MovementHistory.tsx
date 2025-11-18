'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api/client';
import { Clock, MapPin, CheckCircle, XCircle } from 'lucide-react';
import { format } from 'date-fns';

interface Movement {
  timestamp: string;
  target: { x: number; y: number; z: number };
  success: boolean;
  duration?: number;
}

export default function MovementHistory() {
  const [history, setHistory] = useState<Movement[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    setIsLoading(true);
    try {
      const data = await apiClient.getMovementHistory(20);
      setHistory(data.history || []);
    } catch (error) {
      console.error('Failed to load history:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">Historial de Movimientos</h3>
        <button
          onClick={loadHistory}
          disabled={isLoading}
          className="text-sm text-primary-400 hover:text-primary-300 disabled:opacity-50"
        >
          Actualizar
        </button>
      </div>

      <div className="space-y-2 max-h-[400px] overflow-y-auto">
        {isLoading ? (
          <div className="text-center text-gray-400 py-8">Cargando...</div>
        ) : history.length === 0 ? (
          <div className="text-center text-gray-400 py-8">No hay movimientos registrados</div>
        ) : (
          history.map((movement, index) => (
            <div
              key={index}
              className="p-3 bg-gray-700/50 rounded-lg border border-gray-600 hover:border-gray-500 transition-colors"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    {movement.success ? (
                      <CheckCircle className="w-4 h-4 text-green-400" />
                    ) : (
                      <XCircle className="w-4 h-4 text-red-400" />
                    )}
                    <span className="text-sm text-gray-300">
                      {movement.timestamp
                        ? format(new Date(movement.timestamp), 'HH:mm:ss')
                        : 'N/A'}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <MapPin className="w-4 h-4 text-primary-400" />
                    <span className="text-gray-300 font-mono">
                      ({movement.target?.x?.toFixed(3) || 0},{' '}
                      {movement.target?.y?.toFixed(3) || 0},{' '}
                      {movement.target?.z?.toFixed(3) || 0})
                    </span>
                  </div>
                  {movement.duration && (
                    <div className="flex items-center gap-2 mt-1 text-xs text-gray-400">
                      <Clock className="w-3 h-3" />
                      <span>{movement.duration.toFixed(2)}s</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

