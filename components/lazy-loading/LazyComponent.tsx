import React, { Suspense, lazy, ComponentType } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { OptimizedSkeleton } from '../feedback/OptimizedSkeleton';

interface LazyComponentProps {
  fallback?: React.ReactNode;
  errorBoundary?: React.ComponentType<any>;
  onLoad?: () => void;
  onError?: (error: Error) => void;
}

interface LazyComponentConfig {
  loadingFallback?: React.ReactNode;
  errorFallback?: React.ReactNode;
  retryCount?: number;
  retryDelay?: number;
}

const DEFAULT_CONFIG: LazyComponentConfig = {
  loadingFallback: <OptimizedSkeleton variant="card" />,
  errorFallback: <Text>Failed to load component</Text>,
  retryCount: 3,
  retryDelay: 1000,
};

const createLazyComponent = <P extends object>(
  importFunc: () => Promise<{ default: ComponentType<P> }>,
  config: LazyComponentConfig = {}
): React.LazyExoticComponent<ComponentType<P>> => {
  const finalConfig = { ...DEFAULT_CONFIG, ...config };
  
  return lazy(() => 
    importFunc()
      .then(module => {
        finalConfig.onLoad?.();
        return module;
      })
      .catch(error => {
        finalConfig.onError?.(error);
        throw error;
      })
  );
};

const LazyComponent: React.FC<LazyComponentProps> = ({ 
  children, 
  fallback = <OptimizedSkeleton variant="card" />,
  errorBoundary: ErrorBoundary,
  onLoad,
  onError 
}) => {
  const handleLoad = () => {
    onLoad?.();
  };

  const handleError = (error: Error) => {
    onError?.(error);
  };

  const content = (
    <Suspense fallback={fallback}>
      {children}
    </Suspense>
  );

  if (ErrorBoundary) {
    return (
      <ErrorBoundary onError={handleError}>
        {content}
      </ErrorBoundary>
    );
  }

  return content;
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
});

export { createLazyComponent, LazyComponent };
export type { LazyComponentProps, LazyComponentConfig }; 