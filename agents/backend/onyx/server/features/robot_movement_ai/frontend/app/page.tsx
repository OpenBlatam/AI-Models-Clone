'use client';

import { useEffect } from 'react';
import Dashboard from '@/components/Dashboard';
import { useRobotStore } from '@/lib/store/robotStore';
import { toast } from '@/lib/utils/toast';

export default function Home() {
  const { fetchStatus, connectWebSocket, disconnectWebSocket } = useRobotStore();

  useEffect(() => {
    // Fetch initial status
    fetchStatus().catch(() => {
      toast.error('No se pudo conectar con el backend. Verifica que esté corriendo.');
    });

    // Connect WebSocket for real-time chat
    connectWebSocket().catch(() => {
      toast.warning('WebSocket no disponible, usando REST API');
    });

    // Set up polling for status updates
    const statusInterval = setInterval(() => {
      fetchStatus();
    }, 2000);

    // Cleanup
    return () => {
      clearInterval(statusInterval);
      disconnectWebSocket();
    };
  }, [fetchStatus, connectWebSocket, disconnectWebSocket]);

  return (
    <main className="min-h-screen bg-gradient-to-br from-robot-dark via-robot-medium to-robot-light">
      <Dashboard />
    </main>
  );
}

