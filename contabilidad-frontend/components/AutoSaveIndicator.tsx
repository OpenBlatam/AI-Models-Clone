'use client';

import { useState, useEffect } from 'react';

interface AutoSaveIndicatorProps {
  isSaving: boolean;
  lastSaved?: Date;
}

export function AutoSaveIndicator({ isSaving, lastSaved }: AutoSaveIndicatorProps) {
  const [showIndicator, setShowIndicator] = useState(false);

  useEffect(() => {
    if (isSaving) {
      setShowIndicator(true);
      const timer = setTimeout(() => setShowIndicator(false), 2000);
      return () => clearTimeout(timer);
    }
  }, [isSaving]);

  if (!showIndicator && !lastSaved) return null;

  return (
    <div className="fixed bottom-4 right-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg px-3 py-2 text-sm z-40">
      {isSaving ? (
        <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
          <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
          <span>Guardando...</span>
        </div>
      ) : (
        <div className="flex items-center gap-2 text-green-600 dark:text-green-400">
          <span>✓</span>
          <span>Guardado</span>
          {lastSaved && (
            <span className="text-xs text-gray-400 dark:text-gray-500">
              {lastSaved.toLocaleTimeString('es-MX')}
            </span>
          )}
        </div>
      )}
    </div>
  );
}














