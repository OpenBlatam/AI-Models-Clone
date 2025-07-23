'use client';

import React, { Suspense, lazy } from 'react';
import dynamic from 'next/dynamic';

// Next.js dynamic imports with specific options
const AnalyticsDashboard = dynamic(
  () => import('../components/analytics/AnalyticsDashboard'),
  {
    loading: () => <div className="animate-pulse h-32 bg-gray-200 rounded"></div>,
    ssr: false, // Disable SSR for client-only components
    suspense: true
  }
);

const UserProfile = dynamic(
  () => import('../components/user/UserProfile'),
  {
    loading: () => <div className="animate-pulse h-24 bg-gray-200 rounded"></div>,
    ssr: true, // Enable SSR for SEO-friendly components
    suspense: true
  }
);

const SettingsPanel = dynamic(
  () => import('../components/settings/SettingsPanel'),
  {
    loading: () => <div className="animate-pulse h-40 bg-gray-200 rounded"></div>,
    ssr: false,
    suspense: true
  }
);

// Dynamic imports with webpack chunk names
const AdminPanel = dynamic(
  () => import(/* webpackChunkName: "admin" */ '../components/admin/AdminPanel'),
  {
    loading: () => <div className="animate-pulse h-48 bg-gray-200 rounded"></div>,
    ssr: false,
    suspense: true
  }
);

// Conditional dynamic imports
const ChatWidget = dynamic(
  () => import('../components/chat/ChatWidget'),
  {
    loading: () => <div className="animate-pulse h-20 bg-gray-200 rounded"></div>,
    ssr: false,
    suspense: true
  }
);

// Lazy loading with intersection observer
export function LazyLoadOnScroll() {
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
      {isVisible && (
        <Suspense fallback={<div className="animate-pulse h-32 bg-gray-200 rounded"></div>}>
          <AnalyticsDashboard />
        </Suspense>
      )}
    </div>
  );
}

// Route-based lazy loading with Next.js
export function RouteBasedLazyLoading() {
  return (
    <div className="space-y-4">
      <Suspense fallback={<div className="animate-pulse h-32 bg-gray-200 rounded"></div>}>
        <AnalyticsDashboard />
      </Suspense>

      <Suspense fallback={<div className="animate-pulse h-24 bg-gray-200 rounded"></div>}>
        <UserProfile />
      </Suspense>

      <Suspense fallback={<div className="animate-pulse h-40 bg-gray-200 rounded"></div>}>
        <SettingsPanel />
      </Suspense>

      <Suspense fallback={<div className="animate-pulse h-48 bg-gray-200 rounded"></div>}>
        <AdminPanel />
      </Suspense>
    </div>
  );
}

// Lazy loading with user permissions
export function PermissionBasedLazyLoading({ userRole }: { userRole: string }) {
  const AdminComponent = dynamic(
    () => import('../components/admin/AdminPanel'),
    {
      loading: () => <div className="animate-pulse h-48 bg-gray-200 rounded"></div>,
      ssr: false,
      suspense: true
    }
  );

  const UserComponent = dynamic(
    () => import('../components/user/UserPanel'),
    {
      loading: () => <div className="animate-pulse h-32 bg-gray-200 rounded"></div>,
      ssr: true,
      suspense: true
    }
  );

  return (
    <div>
      {userRole === 'admin' ? (
        <Suspense fallback={<div className="animate-pulse h-48 bg-gray-200 rounded"></div>}>
          <AdminComponent />
        </Suspense>
      ) : (
        <Suspense fallback={<div className="animate-pulse h-32 bg-gray-200 rounded"></div>}>
          <UserComponent />
        </Suspense>
      )}
    </div>
  );
}

// Lazy loading with preloading on hover
export function HoverPreloadLazyLoading() {
  const [isPreloaded, setIsPreloaded] = React.useState(false);
  const [isVisible, setIsVisible] = React.useState(false);

  const handleMouseEnter = () => {
    if (!isPreloaded) {
      setIsPreloaded(true);
    }
  };

  const handleClick = () => {
    setIsVisible(true);
  };

  return (
    <div>
      <button
        onMouseEnter={handleMouseEnter}
        onClick={handleClick}
        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
      >
        Load Analytics
      </button>

      {isVisible && isPreloaded && (
        <Suspense fallback={<div className="animate-pulse h-32 bg-gray-200 rounded"></div>}>
          <AnalyticsDashboard />
        </Suspense>
      )}
    </div>
  );
}

// Lazy loading with error handling
export function ErrorHandledLazyLoading() {
  const [hasError, setHasError] = React.useState(false);

  if (hasError) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-md">
        <p className="text-red-600">Failed to load component</p>
        <button
          onClick={() => setHasError(false)}
          className="mt-2 px-3 py-1 bg-red-500 text-white rounded text-sm"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <Suspense 
      fallback={<div className="animate-pulse h-32 bg-gray-200 rounded"></div>}
    >
      <ErrorBoundary onError={() => setHasError(true)}>
        <AnalyticsDashboard />
      </ErrorBoundary>
    </Suspense>
  );
}

// Error boundary component
function ErrorBoundary({ 
  children, 
  onError 
}: { 
  children: React.ReactNode;
  onError: () => void;
}) {
  React.useEffect(() => {
    const handleError = (error: ErrorEvent) => {
      console.error('Component error:', error);
      onError();
    };

    window.addEventListener('error', handleError);
    return () => window.removeEventListener('error', handleError);
  }, [onError]);

  return <>{children}</>;
}

// Lazy loading with performance monitoring
export function PerformanceMonitoredLazyLoading() {
  const [loadTime, setLoadTime] = React.useState<number | null>(null);

  const MonitoredAnalytics = dynamic(
    () => {
      const startTime = performance.now();
      return import('../components/analytics/AnalyticsDashboard').then((module) => {
        const endTime = performance.now();
        setLoadTime(endTime - startTime);
        return module;
      });
    },
    {
      loading: () => <div className="animate-pulse h-32 bg-gray-200 rounded"></div>,
      ssr: false,
      suspense: true
    }
  );

  return (
    <div>
      {loadTime && (
        <div className="text-sm text-gray-500 mb-2">
          Loaded in {loadTime.toFixed(2)}ms
        </div>
      )}
      
      <Suspense fallback={<div className="animate-pulse h-32 bg-gray-200 rounded"></div>}>
        <MonitoredAnalytics />
      </Suspense>
    </div>
  );
}

// Export all components
export {
  AnalyticsDashboard,
  UserProfile,
  SettingsPanel,
  AdminPanel,
  ChatWidget
}; 