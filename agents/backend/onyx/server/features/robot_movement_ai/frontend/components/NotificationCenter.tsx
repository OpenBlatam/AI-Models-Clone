'use client';

import { useState, useEffect } from 'react';
import { Bell, X, CheckCircle, AlertCircle, Info, XCircle } from 'lucide-react';
import { toast } from '@/lib/utils/toast';
import { format } from 'date-fns';

interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
}

export default function NotificationCenter() {
  const [notifications, setNotifications] = useState<Notification[]>([
    {
      id: '1',
      type: 'success',
      title: 'Robot conectado',
      message: 'El robot se ha conectado exitosamente',
      timestamp: new Date(),
      read: false,
    },
    {
      id: '2',
      type: 'warning',
      title: 'Velocidad alta',
      message: 'La velocidad del robot está por encima del límite recomendado',
      timestamp: new Date(Date.now() - 60000),
      read: false,
    },
  ]);
  const [filter, setFilter] = useState<'all' | 'unread' | 'success' | 'error' | 'warning' | 'info'>('all');

  const getIcon = (type: string) => {
    switch (type) {
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'error':
        return <XCircle className="w-5 h-5 text-red-400" />;
      case 'warning':
        return <AlertCircle className="w-5 h-5 text-yellow-400" />;
      case 'info':
        return <Info className="w-5 h-5 text-blue-400" />;
      default:
        return <Bell className="w-5 h-5 text-gray-400" />;
    }
  };

  const getColor = (type: string) => {
    switch (type) {
      case 'success':
        return 'border-green-500/50 bg-green-500/10';
      case 'error':
        return 'border-red-500/50 bg-red-500/10';
      case 'warning':
        return 'border-yellow-500/50 bg-yellow-500/10';
      case 'info':
        return 'border-blue-500/50 bg-blue-500/10';
      default:
        return 'border-gray-500/50 bg-gray-500/10';
    }
  };

  const filteredNotifications = notifications.filter((notif) => {
    if (filter === 'all') return true;
    if (filter === 'unread') return !notif.read;
    return notif.type === filter;
  });

  const unreadCount = notifications.filter((n) => !n.read).length;

  const markAsRead = (id: string) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, read: true } : n))
    );
  };

  const markAllAsRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
    toast.success('Todas las notificaciones marcadas como leídas');
  };

  const deleteNotification = (id: string) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  };

  const clearAll = () => {
    setNotifications([]);
    toast.success('Todas las notificaciones eliminadas');
  };

  return (
    <div className="space-y-6">
      <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-gray-700">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            <Bell className="w-5 h-5 text-primary-400" />
            <h3 className="text-lg font-semibold text-white">Centro de Notificaciones</h3>
            {unreadCount > 0 && (
              <span className="px-2 py-1 bg-red-500 text-white text-xs rounded-full">
                {unreadCount}
              </span>
            )}
          </div>
          <div className="flex gap-2">
            <button
              onClick={markAllAsRead}
              disabled={unreadCount === 0}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Marcar todas como leídas
            </button>
            <button
              onClick={clearAll}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
            >
              Limpiar todo
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="flex gap-2 mb-4 flex-wrap">
          {(['all', 'unread', 'success', 'error', 'warning', 'info'] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1 rounded-lg text-sm transition-colors ${
                filter === f
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {f === 'all' ? 'Todas' : f === 'unread' ? 'No leídas' : f}
            </button>
          ))}
        </div>

        {/* Notifications List */}
        <div className="space-y-2 max-h-[600px] overflow-y-auto">
          {filteredNotifications.length === 0 ? (
            <div className="text-center py-12 text-gray-400">
              <Bell className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>No hay notificaciones</p>
            </div>
          ) : (
            filteredNotifications.map((notif) => (
              <div
                key={notif.id}
                className={`p-4 rounded-lg border ${getColor(notif.type)} ${
                  !notif.read ? 'ring-2 ring-primary-500/50' : ''
                }`}
              >
                <div className="flex items-start gap-3">
                  {getIcon(notif.type)}
                  <div className="flex-1">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <h4 className="font-semibold text-white mb-1">{notif.title}</h4>
                        <p className="text-sm text-gray-300">{notif.message}</p>
                        <p className="text-xs text-gray-400 mt-2">
                          {format(notif.timestamp, 'dd/MM/yyyy HH:mm:ss')}
                        </p>
                      </div>
                      <div className="flex gap-1">
                        {!notif.read && (
                          <button
                            onClick={() => markAsRead(notif.id)}
                            className="p-1 text-gray-400 hover:text-white transition-colors"
                            title="Marcar como leída"
                          >
                            <CheckCircle className="w-4 h-4" />
                          </button>
                        )}
                        <button
                          onClick={() => deleteNotification(notif.id)}
                          className="p-1 text-gray-400 hover:text-red-400 transition-colors"
                          title="Eliminar"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}


