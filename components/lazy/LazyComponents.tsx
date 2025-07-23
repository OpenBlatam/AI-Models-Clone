import React, { Suspense, lazy, Component, ReactNode } from 'react';

// Error Boundary for lazy loaded components
class LazyErrorBoundary extends Component<
  { children: ReactNode; fallback?: ReactNode },
  { hasError: boolean }
> {
  constructor(props: { children: ReactNode; fallback?: ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(): { hasError: boolean } {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    console.error('Lazy component error:', error, errorInfo);
  }

  render(): ReactNode {
    if (this.state.hasError) {
      return this.props.fallback || <div>Something went wrong loading this component.</div>;
    }

    return this.props.children;
  }
}

// Loading component for Suspense fallback
const LoadingSpinner = () => (
  <div className="flex items-center justify-center p-4">
    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
  </div>
);

// Lazy loading wrapper with error boundary
export const withLazyLoading = (
  ComponentLoader: () => Promise<{ default: React.ComponentType<any> }>,
  fallback?: ReactNode
) => {
  const LazyComponent = lazy(ComponentLoader);
  
  return (props: any) => (
    <LazyErrorBoundary fallback={fallback}>
      <Suspense fallback={<LoadingSpinner />}>
        <LazyComponent {...props} />
      </Suspense>
    </LazyErrorBoundary>
  );
};

// Preload function for critical components
export const preloadComponent = (
  ComponentLoader: () => Promise<{ default: React.ComponentType<any> }>
): void => {
  ComponentLoader();
};

// Lazy loading hook for conditional loading
export const useLazyComponent = (
  ComponentLoader: () => Promise<{ default: React.ComponentType<any> }>,
  shouldLoad: boolean
) => {
  const [Component, setComponent] = React.useState<React.ComponentType<any> | null>(null);
  const [isLoading, setIsLoading] = React.useState(false);

  React.useEffect(() => {
    if (shouldLoad && !Component) {
      setIsLoading(true);
      ComponentLoader()
        .then((module) => {
          setComponent(() => module.default);
        })
        .catch((error) => {
          console.error('Failed to load component:', error);
        })
        .finally(() => {
          setIsLoading(false);
        });
    }
  }, [shouldLoad, Component, ComponentLoader]);

  return { Component, isLoading };
}; 

// Example: Lazy load a non-critical component
export const LazyNonCriticalComponent = withLazyLoading(
  () => import('@/components/non-critical/NonCriticalComponent')
); 