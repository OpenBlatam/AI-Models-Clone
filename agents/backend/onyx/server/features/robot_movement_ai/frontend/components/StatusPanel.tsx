'use client';

import { useEffect, useState } from 'react';
import { useRobotStore } from '@/lib/store/robotStore';
import { apiClient } from '@/lib/api/client';
import { RefreshCw, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

export default function StatusPanel() {
  const { status, fetchStatus, isLoading } = useRobotStore();
  const [health, setHealth] = useState<any>(null);
  const [statistics, setStatistics] = useState<any>(null);

  useEffect(() => {
    fetchStatus();
    loadHealth();
    loadStatistics();
  }, [fetchStatus]);

  const loadHealth = async () => {
    try {
      const healthData = await apiClient.getHealth();
      setHealth(healthData);
    } catch (error) {
      console.error('Failed to load health:', error);
    }
  };

  const loadStatistics = async () => {
    try {
      const stats = await apiClient.getStatistics();
      setStatistics(stats);
    } catch (error) {
      console.error('Failed to load statistics:', error);
    }
  };

  const handleRefresh = () => {
    fetchStatus();
    loadHealth();
    loadStatistics();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-semibold text-white">Estado del Sistema</h2>
          <button
            onClick={handleRefresh}
            disabled={isLoading}
            className="flex items-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors disabled:opacity-50"
          >
            <RefreshCw
              className={`w-5 h-5 ${isLoading ? 'animate-spin' : ''}`}
            />
            Actualizar
          </button>
        </div>

        {/* Robot Status */}
        {status && (
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-medium text-white mb-3">
                Estado del Robot
              </h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-gray-700/50 rounded-lg">
                  <p className="text-gray-400 text-sm mb-1">Conexión</p>
                  <div className="flex items-center gap-2">
                    {status.robot_status.connected ? (
                      <CheckCircle className="w-5 h-5 text-green-400" />
                    ) : (
                      <XCircle className="w-5 h-5 text-red-400" />
                    )}
                    <span className="text-white font-medium">
                      {status.robot_status.connected ? 'Conectado' : 'Desconectado'}
                    </span>
                  </div>
                </div>
                <div className="p-4 bg-gray-700/50 rounded-lg">
                  <p className="text-gray-400 text-sm mb-1">Movimiento</p>
                  <div className="flex items-center gap-2">
                    {status.robot_status.moving ? (
                      <AlertCircle className="w-5 h-5 text-yellow-400" />
                    ) : (
                      <CheckCircle className="w-5 h-5 text-green-400" />
                    )}
                    <span className="text-white font-medium">
                      {status.robot_status.moving ? 'En Movimiento' : 'Detenido'}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Position */}
            {status.robot_status.position && (
              <div>
                <h3 className="text-lg font-medium text-white mb-3">Posición</h3>
                <div className="p-4 bg-gray-700/50 rounded-lg">
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <p className="text-gray-400">X</p>
                      <p className="text-white font-medium">
                        {status.robot_status.position.x.toFixed(3)} m
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-400">Y</p>
                      <p className="text-white font-medium">
                        {status.robot_status.position.y.toFixed(3)} m
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-400">Z</p>
                      <p className="text-white font-medium">
                        {status.robot_status.position.z.toFixed(3)} m
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Joint Angles */}
            {status.robot_status.joint_angles && (
              <div>
                <h3 className="text-lg font-medium text-white mb-3">
                  Ángulos de Articulación
                </h3>
                <div className="p-4 bg-gray-700/50 rounded-lg">
                  <div className="grid grid-cols-6 gap-2 text-sm">
                    {status.robot_status.joint_angles.map((angle: number, i: number) => (
                      <div key={i}>
                        <p className="text-gray-400">J{i + 1}</p>
                        <p className="text-white font-medium">
                          {(angle * (180 / Math.PI)).toFixed(1)}°
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Health Status */}
      {health && (
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-medium text-white mb-3">Estado de Salud</h3>
          <div className="space-y-2">
            <div className="flex items-center justify-between p-3 bg-gray-700/50 rounded-lg">
              <span className="text-gray-300">Estado General</span>
              <span
                className={`font-medium ${
                  health.status === 'healthy' ? 'text-green-400' : 'text-red-400'
                }`}
              >
                {health.status}
              </span>
            </div>
            {health.components && (
              <div className="space-y-2">
                {Object.entries(health.components).map(([key, value]: [string, any]) => (
                  <div
                    key={key}
                    className="flex items-center justify-between p-3 bg-gray-700/50 rounded-lg"
                  >
                    <span className="text-gray-300 capitalize">{key}</span>
                    <span
                      className={`font-medium ${
                        value.status === 'healthy' ? 'text-green-400' : 'text-red-400'
                      }`}
                    >
                      {value.status || 'unknown'}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Statistics */}
      {statistics && (
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-medium text-white mb-3">Estadísticas</h3>
          <div className="space-y-2">
            {Object.entries(statistics).map(([key, value]: [string, any]) => (
              <details key={key} className="p-3 bg-gray-700/50 rounded-lg">
                <summary className="text-white font-medium cursor-pointer">
                  {key.replace(/_/g, ' ').toUpperCase()}
                </summary>
                <pre className="mt-2 text-xs text-gray-300 overflow-x-auto">
                  {JSON.stringify(value, null, 2)}
                </pre>
              </details>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

