'use client';

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';
import { useThemeStore } from '@/lib/store/themeStore';
import { Settings, Moon, Sun, Save, RefreshCw, Download, Upload } from 'lucide-react';
import { toast } from '@/lib/utils/toast';
import { exportConfig, importConfig, getDefaultConfig } from '@/lib/utils/configExport';

export default function SettingsPanel() {
  const { theme, toggleTheme, setTheme } = useThemeStore();
  const [config, setConfig] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [pollingInterval, setPollingInterval] = useState(2000);
  const [autoReconnect, setAutoReconnect] = useState(true);

  const handleExportConfig = () => {
    const appConfig = {
      theme,
      pollingInterval,
      autoReconnect,
      apiUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8010',
      preferences: {},
    };
    exportConfig(appConfig);
    toast.success('Configuración exportada');
  };

  const handleImportConfig = async () => {
    const importedConfig = await importConfig();
    if (importedConfig) {
      setTheme(importedConfig.theme);
      setPollingInterval(importedConfig.pollingInterval);
      setAutoReconnect(importedConfig.autoReconnect);
      toast.success('Configuración importada');
    } else {
      toast.error('Error al importar configuración');
    }
  };

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    setIsLoading(true);
    try {
      const data = await apiClient.getConfig();
      setConfig(data);
    } catch (error) {
      console.error('Failed to load config:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveConfig = async (key: string, value: any) => {
    try {
      await apiClient.client.post(`/api/v1/system/config/${key}`, { value });
      toast.success('Configuración guardada');
      loadConfig();
    } catch (error: any) {
      toast.error(`Error: ${error.message || 'Failed to save config'}`);
    }
  };

  return (
    <div className="space-y-6">
      {/* Theme Settings */}
      <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-gray-700">
        <div className="flex items-center gap-2 mb-4">
          <Settings className="w-5 h-5 text-primary-400" />
          <h3 className="text-lg font-semibold text-white">Configuración de Tema</h3>
        </div>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-white font-medium">Modo Oscuro/Claro</p>
            <p className="text-sm text-gray-400">Cambia entre tema oscuro y claro</p>
          </div>
          <button
            onClick={toggleTheme}
            className="flex items-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
          >
            {theme === 'dark' ? <Moon className="w-4 h-4" /> : <Sun className="w-4 h-4" />}
            {theme === 'dark' ? 'Oscuro' : 'Claro'}
          </button>
        </div>
      </div>

      {/* Frontend Settings */}
      <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-4">Configuración del Frontend</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Intervalo de Actualización (ms)
            </label>
            <input
              type="number"
              min="500"
              max="10000"
              step="500"
              value={pollingInterval}
              onChange={(e) => setPollingInterval(parseInt(e.target.value))}
              className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
            <p className="text-xs text-gray-400 mt-1">
              Frecuencia con la que se actualiza el estado del robot
            </p>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-white font-medium">Reconexión Automática</p>
              <p className="text-sm text-gray-400">Reconectar automáticamente si se pierde la conexión</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={autoReconnect}
                onChange={(e) => setAutoReconnect(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-800 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
            </label>
          </div>
        </div>
      </div>

      {/* Backend Config */}
      {config && (
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white">Configuración del Backend</h3>
            <button
              onClick={loadConfig}
              disabled={isLoading}
              className="flex items-center gap-2 px-3 py-1 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
              Actualizar
            </button>
          </div>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {Object.entries(config).map(([key, value]: [string, any]) => (
              <div key={key} className="p-3 bg-gray-700/50 rounded-lg">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-white">{key}</p>
                    <p className="text-xs text-gray-400 font-mono">
                      {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Keyboard Shortcuts */}
      <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-4">Atajos de Teclado</h3>
        <div className="space-y-2">
          <div className="flex items-center justify-between p-2 bg-gray-700/50 rounded">
            <span className="text-gray-300">Ctrl + H</span>
            <span className="text-white">Ir a posición home</span>
          </div>
          <div className="flex items-center justify-between p-2 bg-gray-700/50 rounded">
            <span className="text-gray-300">Ctrl + S</span>
            <span className="text-white">Detener robot</span>
          </div>
          <div className="flex items-center justify-between p-2 bg-gray-700/50 rounded">
            <span className="text-gray-300">Ctrl + R</span>
            <span className="text-white">Iniciar/Detener grabación</span>
          </div>
        </div>
      </div>

      {/* Import/Export */}
      <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-4">Importar/Exportar Configuración</h3>
        <div className="flex gap-3">
          <button
            onClick={handleExportConfig}
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
          >
            <Download className="w-4 h-4" />
            Exportar Configuración
          </button>
          <button
            onClick={handleImportConfig}
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
          >
            <Upload className="w-4 h-4" />
            Importar Configuración
          </button>
        </div>
      </div>
    </div>
  );
}

