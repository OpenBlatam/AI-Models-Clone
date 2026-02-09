import React, { Suspense, lazy } from 'react';

// Lazy load non-critical components
const AnalyticsDashboard = lazy(() => import('./analytics/AnalyticsDashboard'));
const UserProfile = lazy(() => import('./user/UserProfile'));
const SettingsPanel = lazy(() => import('./settings/SettingsPanel'));
const NotificationCenter = lazy(() => import('./notifications/NotificationCenter'));
const ChatWidget = lazy(() => import('./chat/ChatWidget'));
const FileUploader = lazy(() => import('./upload/FileUploader'));
const DataVisualization = lazy(() => import('./charts/DataVisualization'));
const AdminPanel = lazy(() => import('./admin/AdminPanel'));

// Loading fallback components
const LoadingSpinner = () => (
  <div className="flex items-center justify-center p-4">
    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
  </div>
);

const ErrorBoundary = ({ children }: { children: React.ReactNode }) => (
  <div className="p-4 bg-red-50 border border-red-200 rounded-md">
    <p className="text-red-600">Error loading component</p>
    {children}
  </div>
);

// Main component with lazy loading
export function DashboardWithLazyLoading() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-4">
      {/* Critical components loaded immediately */}
      <div className="bg-white p-4 rounded-lg shadow">
        <h2 className="text-lg font-semibold mb-2">Quick Actions</h2>
        {/* Critical content */}
      </div>

      {/* Non-critical components with lazy loading */}
      <Suspense fallback={<LoadingSpinner />}>
        <ErrorBoundary>
          <AnalyticsDashboard />
        </ErrorBoundary>
      </Suspense>

      <Suspense fallback={<LoadingSpinner />}>
        <ErrorBoundary>
          <UserProfile />
        </ErrorBoundary>
      </Suspense>

      <Suspense fallback={<LoadingSpinner />}>
        <ErrorBoundary>
          <SettingsPanel />
        </ErrorBoundary>
      </Suspense>

      <Suspense fallback={<LoadingSpinner />}>
        <ErrorBoundary>
          <NotificationCenter />
        </ErrorBoundary>
      </Suspense>

      <Suspense fallback={<LoadingSpinner />}>
        <ErrorBoundary>
          <ChatWidget />
        </ErrorBoundary>
      </Suspense>

      <Suspense fallback={<LoadingSpinner />}>
        <ErrorBoundary>
          <FileUploader />
        </ErrorBoundary>
      </Suspense>

      <Suspense fallback={<LoadingSpinner />}>
        <ErrorBoundary>
          <DataVisualization />
        </ErrorBoundary>
      </Suspense>

      <Suspense fallback={<LoadingSpinner />}>
        <ErrorBoundary>
          <AdminPanel />
        </ErrorBoundary>
      </Suspense>
    </div>
  );
}

// Route-based lazy loading
export function AppWithRouteLazyLoading() {
  return (
    <div>
      <Suspense fallback={<LoadingSpinner />}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route 
            path="/analytics" 
            element={
              <Suspense fallback={<LoadingSpinner />}>
                <AnalyticsDashboard />
              </Suspense>
            } 
          />
          <Route 
            path="/settings" 
            element={
              <Suspense fallback={<LoadingSpinner />}>
                <SettingsPanel />
              </Suspense>
            } 
          />
          <Route 
            path="/admin" 
            element={
              <Suspense fallback={<LoadingSpinner />}>
                <AdminPanel />
              </Suspense>
            } 
          />
        </Routes>
      </Suspense>
    </div>
  );
}

// Conditional lazy loading based on user permissions
export function ConditionalLazyLoading({ userRole }: { userRole: string }) {
  const AdminComponent = lazy(() => import('./admin/AdminPanel'));
  const UserComponent = lazy(() => import('./user/UserPanel'));

  return (
    <div>
      {userRole === 'admin' ? (
        <Suspense fallback={<LoadingSpinner />}>
          <AdminComponent />
        </Suspense>
      ) : (
        <Suspense fallback={<LoadingSpinner />}>
          <UserComponent />
        </Suspense>
      )}
    </div>
  );
}

// Lazy loading with preloading
export function LazyLoadingWithPreload() {
  const preloadAnalytics = () => {
    const AnalyticsDashboard = lazy(() => import('./analytics/AnalyticsDashboard'));
    // Preload when user hovers over analytics link
  };

  return (
    <div>
      <button 
        onMouseEnter={preloadAnalytics}
        className="p-2 bg-blue-500 text-white rounded"
      >
        Analytics
      </button>
      
      <Suspense fallback={<LoadingSpinner />}>
        <AnalyticsDashboard />
      </Suspense>
    </div>
  );
}

// Lazy loading with retry mechanism
export function LazyLoadingWithRetry() {
  const retryImport = (importFn: () => Promise<any>, retries = 3) => {
    return new Promise((resolve, reject) => {
      importFn()
        .then(resolve)
        .catch((error) => {
          if (retries > 0) {
            setTimeout(() => {
              retryImport(importFn, retries - 1).then(resolve).catch(reject);
            }, 1000);
          } else {
            reject(error);
          }
        });
    });
  };

  const AnalyticsWithRetry = lazy(() => 
    retryImport(() => import('./analytics/AnalyticsDashboard'))
  );

  return (
    <Suspense fallback={<LoadingSpinner />}>
      <ErrorBoundary>
        <AnalyticsWithRetry />
      </ErrorBoundary>
    </Suspense>
  );
}

// Lazy loading with intersection observer for infinite scroll
export function InfiniteScrollWithLazyLoading() {
  const [items, setItems] = React.useState<Array<any>>([]);
  const [loading, setLoading] = React.useState(false);

  const loadMoreItems = async () => {
    setLoading(true);
    // Simulate API call
    const newItems = await fetch('/api/items');
    setItems(prev => [...prev, ...newItems]);
    setLoading(false);
  };

  return (
    <div>
      {items.map((item, index) => (
        <Suspense key={index} fallback={<LoadingSpinner />}>
          <LazyItemComponent item={item} />
        </Suspense>
      ))}
      
      {loading && <LoadingSpinner />}
      
      {/* Intersection observer trigger */}
      <div 
        ref={(el) => {
          if (el) {
            const observer = new IntersectionObserver(
              (entries) => {
                if (entries[0].isIntersecting) {
                  loadMoreItems();
                }
              },
              { threshold: 0.1 }
            );
            observer.observe(el);
          }
        }}
        className="h-4"
      />
    </div>
  );
}

// Lazy loading with webpack chunk names
const AnalyticsDashboard = lazy(() => 
  import(/* webpackChunkName: "analytics" */ './analytics/AnalyticsDashboard')
);

const UserProfile = lazy(() => 
  import(/* webpackChunkName: "user" */ './user/UserProfile')
);

const SettingsPanel = lazy(() => 
  import(/* webpackChunkName: "settings" */ './settings/SettingsPanel')
);

// Export all components
export {
  AnalyticsDashboard,
  UserProfile,
  SettingsPanel,
  NotificationCenter,
  ChatWidget,
  FileUploader,
  DataVisualization,
  AdminPanel
}; 