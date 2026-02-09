'use client';

import { useOnlineStatus } from '@/lib';

export function OfflineIndicator() {
  const isOnline = useOnlineStatus();

  if (isOnline) return null;

  return (
    <div className="fixed bottom-4 left-4 right-4 md:left-auto md:right-4 md:w-auto z-50">
      <div className="bg-yellow-500 text-white px-4 py-3 rounded-lg shadow-lg flex items-center gap-3 animate-slide-in">
        <span className="text-xl">⚠️</span>
        <div>
          <p className="font-semibold">Sin conexión</p>
          <p className="text-sm opacity-90">
            Estás trabajando sin conexión. Algunas funciones pueden no estar disponibles.
          </p>
        </div>
      </div>
    </div>
  );
}





