'use client';

import { useState, useEffect } from 'react';
import { ToastMessage } from './ToastContainer';

interface NotificationCenterProps {
  notifications: ToastMessage[];
  onDismiss: (id: string) => void;
  onDismissAll: () => void;
}

export function NotificationCenter({
  notifications,
  onDismiss,
  onDismissAll,
}: NotificationCenterProps) {
  const [isOpen, setIsOpen] = useState(false);

  if (notifications.length === 0) return null;

  return (
    <>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-4 right-4 bg-blue-600 hover:bg-blue-700 text-white rounded-full w-14 h-14 shadow-lg flex items-center justify-center z-40 transition-transform hover:scale-110"
        aria-label={`Notificaciones (${notifications.length})`}
      >
        <span className="text-xl">🔔</span>
        {notifications.length > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
            {notifications.length > 9 ? '9+' : notifications.length}
          </span>
        )}
      </button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 bg-black bg-opacity-50 z-50"
            onClick={() => setIsOpen(false)}
          />
          <div className="fixed bottom-20 right-4 w-80 md:w-96 bg-white dark:bg-gray-800 rounded-lg shadow-xl z-50 max-h-96 overflow-y-auto">
            <div className="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4 flex justify-between items-center">
              <h3 className="font-bold text-gray-900 dark:text-white">
                Notificaciones ({notifications.length})
              </h3>
              <div className="flex gap-2">
                {notifications.length > 0 && (
                  <button
                    onClick={onDismissAll}
                    className="text-xs text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
                  >
                    Limpiar todo
                  </button>
                )}
                <button
                  onClick={() => setIsOpen(false)}
                  className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                  aria-label="Cerrar"
                >
                  ×
                </button>
              </div>
            </div>
            <div className="p-2">
              {notifications.map((notification) => (
                <div
                  key={notification.id}
                  className="p-3 mb-2 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-900"
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <p className="text-sm text-gray-900 dark:text-white">
                        {notification.message}
                      </p>
                    </div>
                    <button
                      onClick={() => onDismiss(notification.id)}
                      className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 ml-2"
                      aria-label="Cerrar notificación"
                    >
                      ×
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </>
  );
}














