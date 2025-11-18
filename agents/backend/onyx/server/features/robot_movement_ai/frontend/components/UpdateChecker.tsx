'use client';

import { useState, useEffect } from 'react';
import { RefreshCw, Download, CheckCircle, AlertCircle } from 'lucide-react';
import { toast } from '@/lib/utils/toast';

interface UpdateInfo {
  currentVersion: string;
  latestVersion: string;
  updateAvailable: boolean;
  releaseNotes?: string;
  downloadUrl?: string;
}

export default function UpdateChecker() {
  const [updateInfo, setUpdateInfo] = useState<UpdateInfo>({
    currentVersion: '1.0.0',
    latestVersion: '1.0.0',
    updateAvailable: false,
  });
  const [isChecking, setIsChecking] = useState(false);
  const [lastChecked, setLastChecked] = useState<Date | null>(null);

  const checkForUpdates = async () => {
    setIsChecking(true);
    try {
      // Simulate update check
      await new Promise((resolve) => setTimeout(resolve, 2000));
      
      const mockUpdate: UpdateInfo = {
        currentVersion: '1.0.0',
        latestVersion: '1.1.0',
        updateAvailable: true,
        releaseNotes: 'Nuevas características:\n- Mejoras en rendimiento\n- Nuevos componentes\n- Corrección de bugs',
        downloadUrl: 'https://example.com/download',
      };
      
      setUpdateInfo(mockUpdate);
      setLastChecked(new Date());
      if (mockUpdate.updateAvailable) {
        toast.info('Actualización disponible');
      } else {
        toast.success('Estás usando la última versión');
      }
    } catch (error: any) {
      toast.error(`Error: ${error.message || 'Failed to check for updates'}`);
    } finally {
      setIsChecking(false);
    }
  };

  useEffect(() => {
    checkForUpdates();
  }, []);

  return (
    <div className="space-y-6">
      <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-gray-700">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            <RefreshCw className="w-5 h-5 text-primary-400" />
            <h3 className="text-lg font-semibold text-white">Verificador de Actualizaciones</h3>
          </div>
          <button
            onClick={checkForUpdates}
            disabled={isChecking}
            className="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${isChecking ? 'animate-spin' : ''}`} />
            Verificar
          </button>
        </div>

        {/* Version Info */}
        <div className="mb-6 p-4 bg-gray-700/50 rounded-lg border border-gray-600">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-400 mb-1">Versión Actual</p>
              <p className="text-lg font-bold text-white">{updateInfo.currentVersion}</p>
            </div>
            <div>
              <p className="text-sm text-gray-400 mb-1">Última Versión</p>
              <p className="text-lg font-bold text-white">{updateInfo.latestVersion}</p>
            </div>
          </div>
          {lastChecked && (
            <p className="text-xs text-gray-400 mt-3">
              Última verificación: {lastChecked.toLocaleString('es-ES')}
            </p>
          )}
        </div>

        {/* Update Status */}
        {updateInfo.updateAvailable ? (
          <div className="p-4 bg-yellow-500/10 border border-yellow-500/50 rounded-lg">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-yellow-400 mt-0.5" />
              <div className="flex-1">
                <h4 className="font-semibold text-yellow-400 mb-2">Actualización Disponible</h4>
                {updateInfo.releaseNotes && (
                  <div className="mb-3">
                    <p className="text-sm text-gray-300 whitespace-pre-line">
                      {updateInfo.releaseNotes}
                    </p>
                  </div>
                )}
                {updateInfo.downloadUrl && (
                  <a
                    href={updateInfo.downloadUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white rounded-lg transition-colors"
                  >
                    <Download className="w-4 h-4" />
                    Descargar Actualización
                  </a>
                )}
              </div>
            </div>
          </div>
        ) : (
          <div className="p-4 bg-green-500/10 border border-green-500/50 rounded-lg">
            <div className="flex items-center gap-3">
              <CheckCircle className="w-5 h-5 text-green-400" />
              <p className="text-green-400 font-medium">
                Estás usando la última versión disponible
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}


