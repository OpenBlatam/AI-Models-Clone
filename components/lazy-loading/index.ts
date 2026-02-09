import { lazy, Suspense, ComponentType, ReactNode } from 'react';

// Lazy loading wrapper with error boundary
export const createLazyComponent = <T extends ComponentType<any>>(
  importFunc: () => Promise<{ default: T }>,
  fallback?: ReactNode
) => {
  const LazyComponent = lazy(importFunc);
  
  return (props: React.ComponentProps<T>) => (
    <Suspense fallback={fallback || <div>Loading...</div>}>
      <LazyComponent {...props} />
    </Suspense>
  );
};

// Preload function for critical components
export const preloadComponent = <T extends ComponentType<any>>(
  importFunc: () => Promise<{ default: T }>
) => {
  return () => {
    importFunc();
  };
};

// Lazy loading with retry mechanism
export const createLazyComponentWithRetry = <T extends ComponentType<any>>(
  importFunc: () => Promise<{ default: T }>,
  retries = 3,
  fallback?: ReactNode
) => {
  const LazyComponent = lazy(() => {
    return new Promise((resolve, reject) => {
      let attempts = 0;
      
      const attemptLoad = () => {
        importFunc()
          .then(resolve)
          .catch((error) => {
            attempts++;
            if (attempts < retries) {
              setTimeout(attemptLoad, 1000 * attempts);
            } else {
              reject(error);
            }
          });
      };
      
      attemptLoad();
    });
  });
  
  return (props: React.ComponentProps<T>) => (
    <Suspense fallback={fallback || <div>Loading...</div>}>
      <LazyComponent {...props} />
    </Suspense>
  );
}; 