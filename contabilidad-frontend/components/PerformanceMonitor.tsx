'use client';

import { useEffect, useState } from 'react';

interface PerformanceMetrics {
  loadTime: number;
  renderTime: number;
  memoryUsage?: number;
}

export function PerformanceMonitor({ enabled = false }: { enabled?: boolean }) {
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);

  useEffect(() => {
    if (!enabled || typeof window === 'undefined') return;

    const measurePerformance = () => {
      if (performance.timing) {
        const loadTime =
          performance.timing.loadEventEnd - performance.timing.navigationStart;
        const renderTime =
          performance.timing.domContentLoadedEventEnd -
          performance.timing.navigationStart;

        const memory = (performance as any).memory
          ? {
              used: (performance as any).memory.usedJSHeapSize / 1048576,
              total: (performance as any).memory.totalJSHeapSize / 1048576,
            }
          : undefined;

        setMetrics({
          loadTime,
          renderTime,
          memoryUsage: memory?.used,
        });
      }
    };

    // Medir después de que la página cargue
    if (document.readyState === 'complete') {
      measurePerformance();
    } else {
      window.addEventListener('load', measurePerformance);
      return () => window.removeEventListener('load', measurePerformance);
    }
  }, [enabled]);

  if (!enabled || !metrics) return null;

  return (
    <div className="fixed bottom-4 right-4 bg-black/80 text-white text-xs p-2 rounded font-mono z-50">
      <div>Load: {metrics.loadTime}ms</div>
      <div>Render: {metrics.renderTime}ms</div>
      {metrics.memoryUsage && (
        <div>Memory: {metrics.memoryUsage.toFixed(2)}MB</div>
      )}
    </div>
  );
}














