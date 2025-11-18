'use client';

import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Settings, User, Bell, Shield, Globe } from 'lucide-react';
import toast from 'react-hot-toast';

export default function SettingsPage() {
  const [apiUrl, setApiUrl] = useState(
    typeof window !== 'undefined'
      ? localStorage.getItem('api_url') || 'http://localhost:8006'
      : 'http://localhost:8006'
  );
  const [notifications, setNotifications] = useState({
    email: true,
    push: false,
    alerts: true,
  });

  const handleSaveApiUrl = () => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('api_url', apiUrl);
      toast.success('URL de API guardada');
    }
  };

  const handleSaveNotifications = () => {
    toast.success('Preferencias de notificaciones guardadas');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <div className="flex items-center space-x-3 mb-2">
            <Settings className="h-8 w-8 text-primary-600" />
            <h1 className="text-3xl font-bold text-gray-900">Configuración</h1>
          </div>
          <p className="text-gray-600">
            Gestiona tus preferencias y configuración de la aplicación
          </p>
        </div>

        <div className="space-y-6">
          {/* API Configuration */}
          <Card>
            <CardHeader>
              <div className="flex items-center space-x-2">
                <Globe className="h-5 w-5 text-primary-600" />
                <CardTitle>Configuración de API</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    URL del Backend
                  </label>
                  <input
                    type="text"
                    value={apiUrl}
                    onChange={(e) => setApiUrl(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="http://localhost:8006"
                  />
                  <p className="mt-1 text-sm text-gray-500">
                    URL base del servidor de la API
                  </p>
                </div>
                <Button onClick={handleSaveApiUrl}>Guardar</Button>
              </div>
            </CardContent>
          </Card>

          {/* Notifications */}
          <Card>
            <CardHeader>
              <div className="flex items-center space-x-2">
                <Bell className="h-5 w-5 text-primary-600" />
                <CardTitle>Notificaciones</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">Notificaciones por Email</p>
                    <p className="text-sm text-gray-500">
                      Recibe actualizaciones por correo electrónico
                    </p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={notifications.email}
                      onChange={(e) =>
                        setNotifications({ ...notifications, email: e.target.checked })
                      }
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                  </label>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">Notificaciones Push</p>
                    <p className="text-sm text-gray-500">
                      Recibe notificaciones en tiempo real
                    </p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={notifications.push}
                      onChange={(e) =>
                        setNotifications({ ...notifications, push: e.target.checked })
                      }
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                  </label>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">Alertas Importantes</p>
                    <p className="text-sm text-gray-500">
                      Recibe alertas sobre condiciones detectadas
                    </p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={notifications.alerts}
                      onChange={(e) =>
                        setNotifications({ ...notifications, alerts: e.target.checked })
                      }
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                  </label>
                </div>

                <Button onClick={handleSaveNotifications}>Guardar Preferencias</Button>
              </div>
            </CardContent>
          </Card>

          {/* About */}
          <Card>
            <CardHeader>
              <div className="flex items-center space-x-2">
                <Shield className="h-5 w-5 text-primary-600" />
                <CardTitle>Acerca de</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <p className="text-gray-700">
                  <strong>Versión:</strong> 1.0.0
                </p>
                <p className="text-gray-700">
                  <strong>Backend API:</strong> Dermatology AI v5.5.0
                </p>
                <p className="text-sm text-gray-500 mt-4">
                  Sistema avanzado de IA para análisis de calidad de piel y recomendaciones
                  personalizadas de skincare.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

