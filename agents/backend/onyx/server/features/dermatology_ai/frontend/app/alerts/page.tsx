'use client';

import React, { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api/client';
import { Alert, AlertsResponse } from '@/lib/types/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Loading } from '@/components/ui/Loading';
import { Bell, AlertCircle, CheckCircle, XCircle, Info } from 'lucide-react';
import toast from 'react-hot-toast';
import { useAuth } from '@/lib/contexts/AuthContext';
import { format } from 'date-fns';

export default function AlertsPage() {
  const { user } = useAuth();
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    if (user) {
      loadAlerts();
    }
  }, [user]);

  const loadAlerts = async () => {
    if (!user) return;
    setIsLoading(true);
    try {
      const [alertsResponse, summaryResponse] = await Promise.all([
        apiClient.getAlerts(user.id),
        apiClient.getAlertsSummary(user.id),
      ]);
      setAlerts(alertsResponse.alerts || []);
      setUnreadCount(summaryResponse.unread_count || 0);
    } catch (error: any) {
      toast.error(error.message || 'Error al cargar alertas');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAcknowledge = async (alertId: string) => {
    if (!user) return;
    try {
      await apiClient.acknowledgeAlert(user.id, alertId);
      toast.success('Alerta marcada como leída');
      loadAlerts();
    } catch (error: any) {
      toast.error(error.message || 'Error al marcar alerta');
    }
  };

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'condition_detected':
        return <AlertCircle className="h-5 w-5 text-red-600" />;
      case 'score_drop':
        return <XCircle className="h-5 w-5 text-yellow-600" />;
      case 'recommendation':
        return <Info className="h-5 w-5 text-blue-600" />;
      case 'reminder':
        return <Bell className="h-5 w-5 text-purple-600" />;
      default:
        return <Info className="h-5 w-5 text-gray-600" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200 dark:bg-red-900 dark:text-red-200 dark:border-red-800';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200 dark:bg-orange-900 dark:text-orange-200 dark:border-orange-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200 dark:bg-yellow-900 dark:text-yellow-200 dark:border-yellow-800';
      default:
        return 'bg-blue-100 text-blue-800 border-blue-200 dark:bg-blue-900 dark:text-blue-200 dark:border-blue-800';
    }
  };

  const getTypeLabel = (type: string) => {
    switch (type) {
      case 'condition_detected':
        return 'Condición Detectada';
      case 'score_drop':
        return 'Caída de Puntuación';
      case 'recommendation':
        return 'Recomendación';
      case 'reminder':
        return 'Recordatorio';
      default:
        return type;
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <Card className="p-8 text-center">
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Por favor inicia sesión para ver tus alertas
          </p>
          <Button href="/">Ir al inicio</Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-3">
              <Bell className="h-8 w-8 text-primary-600 dark:text-primary-400" />
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                Alertas
              </h1>
            </div>
            {unreadCount > 0 && (
              <div className="px-3 py-1 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 rounded-full text-sm font-medium">
                {unreadCount} sin leer
              </div>
            )}
          </div>
          <p className="text-gray-600 dark:text-gray-400">
            Mantente al día con las alertas importantes sobre tu piel
          </p>
        </div>

        {isLoading ? (
          <Loading fullScreen text="Cargando alertas..." />
        ) : alerts.length === 0 ? (
          <Card className="p-12 text-center">
            <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-700 dark:text-gray-300 mb-2">
              No hay alertas
            </h3>
            <p className="text-gray-500 dark:text-gray-400">
              ¡Todo está bien! No tienes alertas pendientes.
            </p>
          </Card>
        ) : (
          <div className="space-y-4">
            {alerts.map((alert) => (
              <Card
                key={alert.alert_id}
                className={`transition-all ${
                  !alert.acknowledged
                    ? 'border-l-4 border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                    : 'opacity-75'
                }`}
              >
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-4 flex-1">
                      <div className="mt-1">{getAlertIcon(alert.type)}</div>
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                            {alert.title}
                          </h3>
                          <span
                            className={`px-2 py-1 text-xs font-medium rounded border ${getSeverityColor(
                              alert.severity
                            )}`}
                          >
                            {alert.severity}
                          </span>
                          <span className="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded">
                            {getTypeLabel(alert.type)}
                          </span>
                        </div>
                        <p className="text-gray-700 dark:text-gray-300 mb-3">
                          {alert.message}
                        </p>
                        {alert.action_required && (
                          <div className="mb-3 p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded">
                            <p className="text-sm font-medium text-yellow-800 dark:text-yellow-200">
                              Acción requerida:
                            </p>
                            <p className="text-sm text-yellow-700 dark:text-yellow-300 mt-1">
                              {alert.action_required}
                            </p>
                          </div>
                        )}
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          {format(new Date(alert.timestamp), "d 'de' MMMM, yyyy 'a las' HH:mm")}
                        </p>
                      </div>
                    </div>
                    {!alert.acknowledged && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleAcknowledge(alert.alert_id)}
                        className="ml-4"
                      >
                        Marcar como leída
                      </Button>
                    )}
                    {alert.acknowledged && (
                      <div className="ml-4 flex items-center text-green-600 dark:text-green-400">
                        <CheckCircle className="h-5 w-5 mr-1" />
                        <span className="text-sm">Leída</span>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

