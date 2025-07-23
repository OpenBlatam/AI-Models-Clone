import React, { Suspense, lazy } from 'react';

// Lazy load non-critical dashboard components
const AnalyticsChart = lazy(() => import('../charts/AnalyticsChart'));
const PerformanceMetrics = lazy(() => import('../performance/PerformanceMetrics'));
const UserActivity = lazy(() => import('../dashboard/UserActivity'));
const NotificationCenter = lazy(() => import('../dashboard/NotificationCenter'));
const AdvancedFilters = lazy(() => import('../dashboard/AdvancedFilters'));
const DataExport = lazy(() => import('../dashboard/DataExport'));
const SettingsPanel = lazy(() => import('../dashboard/SettingsPanel'));

// Loading fallback component
const DashboardLoading = () => (
  <div className="flex items-center justify-center h-32">
    <div className="animate-pulse space-y-4 w-full max-w-md">
      <div className="h-4 bg-gray-200 rounded w-3/4"></div>
      <div className="h-4 bg-gray-200 rounded w-1/2"></div>
      <div className="h-4 bg-gray-200 rounded w-5/6"></div>
    </div>
  </div>
);

// Error fallback component
const DashboardError = () => (
  <div className="flex items-center justify-center h-32 text-red-600">
    <div className="text-center">
      <div className="text-lg font-semibold">Failed to load dashboard component</div>
      <button 
        onClick={() => window.location.reload()} 
        className="mt-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
      >
        Retry
      </button>
    </div>
  </div>
);

// Lazy Dashboard Container
export const LazyDashboardContainer: React.FC<{ showAdvanced?: boolean }> = ({ showAdvanced = false }) => {
  return (
    <div className="space-y-6">
      {/* Critical components loaded immediately */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-2">Quick Stats</h3>
          {/* Critical stats component */}
        </div>
      </div>

      {/* Lazy loaded non-critical components */}
      <Suspense fallback={<DashboardLoading />}>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">Analytics</h3>
            <AnalyticsChart />
          </div>
          
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">Performance</h3>
            <PerformanceMetrics />
          </div>
        </div>
      </Suspense>

      {/* Conditionally loaded advanced components */}
      {showAdvanced && (
        <Suspense fallback={<DashboardLoading />}>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="bg-white p-4 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-4">User Activity</h3>
              <UserActivity />
            </div>
            
            <div className="bg-white p-4 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-4">Notifications</h3>
              <NotificationCenter />
            </div>
            
            <div className="bg-white p-4 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-4">Advanced Filters</h3>
              <AdvancedFilters />
            </div>
          </div>
        </Suspense>
      )}

      {/* Utility components loaded on demand */}
      <Suspense fallback={<DashboardLoading />}>
        <div className="flex space-x-4">
          <DataExport />
          <SettingsPanel />
        </div>
      </Suspense>
    </div>
  );
};

// Lazy loading with intersection observer
export const LazyOnScroll: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isVisible, setIsVisible] = React.useState(false);
  const ref = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect();
        }
      },
      { threshold: 0.1 }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => observer.disconnect();
  }, []);

  return (
    <div ref={ref}>
      {isVisible ? (
        <Suspense fallback={<DashboardLoading />}>
          {children}
        </Suspense>
      ) : (
        <DashboardLoading />
      )}
    </div>
  );
}; 