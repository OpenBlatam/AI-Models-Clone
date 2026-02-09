'use client';

import { usePreferences } from '@/lib/hooks/usePreferences';
import { Button } from './Button';

interface PreferencesModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function PreferencesModal({ isOpen, onClose }: PreferencesModalProps) {
  const { preferences, updatePreference, resetPreferences } = usePreferences();

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-6 flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Preferencias
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 text-2xl"
            aria-label="Cerrar"
          >
            ×
          </button>
        </div>

        <div className="p-6 space-y-6">
          <section>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Apariencia
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Tema
                </label>
                <select
                  value={preferences.theme}
                  onChange={(e) =>
                    updatePreference('theme', e.target.value as 'light' | 'dark' | 'auto')
                  }
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option value="auto">Automático</option>
                  <option value="light">Claro</option>
                  <option value="dark">Oscuro</option>
                </select>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Animaciones
                  </label>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Habilitar animaciones y transiciones
                  </p>
                </div>
                <button
                  onClick={() => updatePreference('animations', !preferences.animations)}
                  className={`relative w-12 h-6 rounded-full transition-colors ${
                    preferences.animations ? 'bg-blue-600' : 'bg-gray-300'
                  }`}
                >
                  <span
                    className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform ${
                      preferences.animations ? 'translate-x-6' : 'translate-x-0'
                    }`}
                  ></span>
                </button>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Modo Compacto
                  </label>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Mostrar más información en menos espacio
                  </p>
                </div>
                <button
                  onClick={() => updatePreference('compactMode', !preferences.compactMode)}
                  className={`relative w-12 h-6 rounded-full transition-colors ${
                    preferences.compactMode ? 'bg-blue-600' : 'bg-gray-300'
                  }`}
                >
                  <span
                    className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform ${
                      preferences.compactMode ? 'translate-x-6' : 'translate-x-0'
                    }`}
                  ></span>
                </button>
              </div>
            </div>
          </section>

          <section>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Funcionalidad
            </h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Notificaciones
                  </label>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Mostrar notificaciones toast
                  </p>
                </div>
                <button
                  onClick={() => updatePreference('notifications', !preferences.notifications)}
                  className={`relative w-12 h-6 rounded-full transition-colors ${
                    preferences.notifications ? 'bg-blue-600' : 'bg-gray-300'
                  }`}
                >
                  <span
                    className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform ${
                      preferences.notifications ? 'translate-x-6' : 'translate-x-0'
                    }`}
                  ></span>
                </button>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Guardado Automático
                  </label>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Guardar automáticamente los formularios
                  </p>
                </div>
                <button
                  onClick={() => updatePreference('autoSave', !preferences.autoSave)}
                  className={`relative w-12 h-6 rounded-full transition-colors ${
                    preferences.autoSave ? 'bg-blue-600' : 'bg-gray-300'
                  }`}
                >
                  <span
                    className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform ${
                      preferences.autoSave ? 'translate-x-6' : 'translate-x-0'
                    }`}
                  ></span>
                </button>
              </div>
            </div>
          </section>

          <section>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Idioma
            </h3>
            <select
              value={preferences.language}
              onChange={(e) => updatePreference('language', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="es">Español</option>
              <option value="en">English</option>
            </select>
          </section>
        </div>

        <div className="sticky bottom-0 bg-gray-50 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 p-4 flex justify-between">
          <Button variant="ghost" onClick={resetPreferences}>
            Restablecer
          </Button>
          <Button onClick={onClose}>Cerrar</Button>
        </div>
      </div>
    </div>
  );
}














