import { lazy, ComponentType } from 'react';

// Type for lazy loading with retry
interface LazyLoadOptions {
  retries?: number;
  delay?: number;
  chunkName?: string;
}

// Retry mechanism for failed imports
export function createLazyComponentWithRetry<T extends ComponentType<any>>(
  importFn: () => Promise<{ default: T }>,
  options: LazyLoadOptions = {}
): React.LazyExoticComponent<T> {
  const { retries = 3, delay = 1000 } = options;

  const retryImport = (attempts: number): Promise<{ default: T }> => {
    return importFn().catch((error) => {
      if (attempts > 0) {
        return new Promise((resolve) => {
          setTimeout(() => {
            retryImport(attempts - 1).then(resolve).catch(() => {
              throw error;
            });
          }, delay);
        });
      }
      throw error;
    });
  };

  return lazy(() => retryImport(retries));
}

// Preload utility for components
export function preloadComponent<T extends ComponentType<any>>(
  importFn: () => Promise<{ default: T }>
): Promise<{ default: T }> {
  return importFn();
}

// Lazy loading with webpack chunk names
export function createNamedLazyComponent<T extends ComponentType<any>>(
  importFn: () => Promise<{ default: T }>,
  chunkName: string
): React.LazyExoticComponent<T> {
  return lazy(() => 
    importFn().then(module => ({
      default: module.default
    }))
  );
}

// Conditional lazy loading based on feature flags
export function createConditionalLazyComponent<T extends ComponentType<any>>(
  importFn: () => Promise<{ default: T }>,
  condition: () => boolean
): React.LazyExoticComponent<T> | null {
  if (!condition()) {
    return null;
  }
  
  return lazy(importFn);
}

// Lazy loading with loading states
export interface LazyLoadingState {
  loading: boolean;
  error: Error | null;
  component: React.ComponentType<any> | null;
}

export function useLazyComponent<T extends ComponentType<any>>(
  importFn: () => Promise<{ default: T }>
): LazyLoadingState {
  const [state, setState] = React.useState<LazyLoadingState>({
    loading: true,
    error: null,
    component: null
  });

  React.useEffect(() => {
    importFn()
      .then((module) => {
        setState({
          loading: false,
          error: null,
          component: module.default
        });
      })
      .catch((error) => {
        setState({
          loading: false,
          error,
          component: null
        });
      });
  }, [importFn]);

  return state;
}

// Intersection observer for lazy loading
export function useIntersectionObserver(
  callback: () => void,
  options: IntersectionObserverInit = {}
) {
  const observerRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          callback();
        }
      });
    }, options);

    if (observerRef.current) {
      observer.observe(observerRef.current);
    }

    return () => {
      if (observerRef.current) {
        observer.unobserve(observerRef.current);
      }
    };
  }, [callback, options]);

  return observerRef;
}

// Lazy loading with error boundaries
export function withErrorBoundary<T extends ComponentType<any>>(
  Component: React.LazyExoticComponent<T>,
  fallback?: React.ComponentType<any>
) {
  return function ErrorBoundaryWrapper(props: any) {
    return (
      <ErrorBoundary fallback={fallback}>
        <Component {...props} />
      </ErrorBoundary>
    );
  };
}

// Error boundary component
export function ErrorBoundary({ 
  children, 
  fallback 
}: { 
  children: React.ReactNode;
  fallback?: React.ComponentType<any>;
}) {
  const [hasError, setHasError] = React.useState(false);

  React.useEffect(() => {
    const handleError = (error: Error) => {
      console.error('Lazy loading error:', error);
      setHasError(true);
    };

    window.addEventListener('error', handleError);
    return () => window.removeEventListener('error', handleError);
  }, []);

  if (hasError) {
    return fallback ? <fallback /> : (
      <div className="p-4 bg-red-50 border border-red-200 rounded-md">
        <p className="text-red-600">Error loading component</p>
      </div>
    );
  }

  return <>{children}</>;
}

// Loading spinner component
export function LoadingSpinner({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12'
  };

  return (
    <div className="flex items-center justify-center p-4">
      <div className={`animate-spin rounded-full border-b-2 border-blue-600 ${sizeClasses[size]}`}></div>
    </div>
  );
}

// Skeleton loading component
export function SkeletonLoader({ lines = 3 }: { lines?: number }) {
  return (
    <div className="animate-pulse">
      {Array.from({ length: lines }).map((_, index) => (
        <div
          key={index}
          className="h-4 bg-gray-200 rounded mb-2"
          style={{ width: `${Math.random() * 40 + 60}%` }}
        />
      ))}
    </div>
  );
}

// Lazy loading with performance monitoring
export function createLazyComponentWithMonitoring<T extends ComponentType<any>>(
  importFn: () => Promise<{ default: T }>,
  componentName: string
): React.LazyExoticComponent<T> {
  return lazy(async () => {
    const startTime = performance.now();
    
    try {
      const module = await importFn();
      const loadTime = performance.now() - startTime;
      
      // Log performance metrics
      console.log(`${componentName} loaded in ${loadTime.toFixed(2)}ms`);
      
      return module;
    } catch (error) {
      const loadTime = performance.now() - startTime;
      console.error(`${componentName} failed to load after ${loadTime.toFixed(2)}ms:`, error);
      throw error;
    }
  });
}

// Export all utilities
export {
  createLazyComponentWithRetry,
  preloadComponent,
  createNamedLazyComponent,
  createConditionalLazyComponent,
  useLazyComponent,
  useIntersectionObserver,
  withErrorBoundary,
  ErrorBoundary,
  LoadingSpinner,
  SkeletonLoader,
  createLazyComponentWithMonitoring
}; 