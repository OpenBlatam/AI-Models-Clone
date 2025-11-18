'use client';

import { useState } from 'react';
import { apiClient } from '@/lib/api/client';
import { useRobotStore } from '@/lib/store/robotStore';
import { Sparkles, Play, Download } from 'lucide-react';
import { toast } from '@/lib/utils/toast';

type Algorithm = 'astar' | 'rrt';

export default function TrajectoryOptimizer() {
  const { currentPosition } = useRobotStore();
  const [target, setTarget] = useState({ x: 0.5, y: 0.3, z: 0.2 });
  const [algorithm, setAlgorithm] = useState<Algorithm>('astar');
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleOptimize = async () => {
    if (!currentPosition) {
      toast.error('No hay posición actual disponible');
      return;
    }

    setIsOptimizing(true);
    try {
      let data;
      if (algorithm === 'astar') {
        data = await apiClient.optimizeAStar(target, 0.05);
      } else {
        data = await apiClient.optimizeRRT(target, 1000, 0.1);
      }
      setResult(data);
      toast.success(`Trayectoria optimizada con ${algorithm.toUpperCase()}`);
    } catch (error: any) {
      toast.error(`Error: ${error.message || 'Failed to optimize trajectory'}`);
    } finally {
      setIsOptimizing(false);
    }
  };

  const handleExport = async () => {
    if (!result) return;

    try {
      const waypoints = [
        { x: currentPosition!.x, y: currentPosition!.y, z: currentPosition!.z },
        target,
      ];
      const data = await apiClient.exportTrajectory({ waypoints }, 'json');
      toast.success(`Trayectoria exportada: ${data.filepath}`);
    } catch (error: any) {
      toast.error(`Error: ${error.message || 'Failed to export trajectory'}`);
    }
  };

  return (
    <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-gray-700">
      <div className="flex items-center gap-2 mb-6">
        <Sparkles className="w-5 h-5 text-primary-400" />
        <h3 className="text-lg font-semibold text-white">Optimización de Trayectoria</h3>
      </div>

      <div className="space-y-4">
        {/* Algorithm Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Algoritmo
          </label>
          <div className="flex gap-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                value="astar"
                checked={algorithm === 'astar'}
                onChange={(e) => setAlgorithm(e.target.value as Algorithm)}
                className="text-primary-500"
              />
              <span className="text-white">A*</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                value="rrt"
                checked={algorithm === 'rrt'}
                onChange={(e) => setAlgorithm(e.target.value as Algorithm)}
                className="text-primary-500"
              />
              <span className="text-white">RRT</span>
            </label>
          </div>
        </div>

        {/* Target Position */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Posición Objetivo
          </label>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <input
                type="number"
                step="0.01"
                value={target.x}
                onChange={(e) => setTarget({ ...target, x: parseFloat(e.target.value) || 0 })}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                placeholder="X"
              />
            </div>
            <div>
              <input
                type="number"
                step="0.01"
                value={target.y}
                onChange={(e) => setTarget({ ...target, y: parseFloat(e.target.value) || 0 })}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                placeholder="Y"
              />
            </div>
            <div>
              <input
                type="number"
                step="0.01"
                value={target.z}
                onChange={(e) => setTarget({ ...target, z: parseFloat(e.target.value) || 0 })}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                placeholder="Z"
              />
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          <button
            onClick={handleOptimize}
            disabled={isOptimizing || !currentPosition}
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Play className="w-4 h-4" />
            {isOptimizing ? 'Optimizando...' : 'Optimizar'}
          </button>
          {result && (
            <button
              onClick={handleExport}
              className="flex items-center justify-center gap-2 px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white font-medium rounded-lg transition-colors"
            >
              <Download className="w-4 h-4" />
              Exportar
            </button>
          )}
        </div>

        {/* Results */}
        {result && (
          <div className="mt-4 p-4 bg-gray-700/50 rounded-lg border border-gray-600">
            <h4 className="text-sm font-medium text-white mb-2">Resultados</h4>
            <div className="space-y-1 text-sm text-gray-300">
              <div>
                <span className="text-gray-400">Puntos de trayectoria: </span>
                <span className="text-white font-mono">{result.trajectory_points || 0}</span>
              </div>
              {result.analysis && (
                <>
                  <div>
                    <span className="text-gray-400">Distancia total: </span>
                    <span className="text-white font-mono">
                      {result.analysis.total_distance?.toFixed(3) || 'N/A'} m
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-400">Tiempo estimado: </span>
                    <span className="text-white font-mono">
                      {result.analysis.estimated_time?.toFixed(2) || 'N/A'} s
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-400">Sin colisiones: </span>
                    <span
                      className={`font-mono ${
                        result.analysis.collision_free ? 'text-green-400' : 'text-red-400'
                      }`}
                    >
                      {result.analysis.collision_free ? 'Sí' : 'No'}
                    </span>
                  </div>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

