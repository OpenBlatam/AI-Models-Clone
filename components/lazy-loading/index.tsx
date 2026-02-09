import React, { Suspense, lazy, ComponentType } from 'react';

// Lazy loading wrapper with error boundary
interface LazyComponentProps {
  fallback?: React.ReactNode;
  errorFallback?: React.ReactNode;
}

// Error boundary for lazy components
class LazyErrorBoundary extends React.Component<
  { children: React.ReactNode; fallback: React.ReactNode },
  { hasError: boolean }
> {
  constructor(props: { children: React.ReactNode; fallback: React.ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(): { hasError: boolean } {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    console.error('Lazy component error:', error, errorInfo);
  }

  render(): React.ReactNode {
    if (this.state.hasError) {
      return this.props.fallback;
    }
    return this.props.children;
  }
}

// Lazy component wrapper
export function createLazyComponent<T extends object>(
  importFunc: () => Promise<{ default: ComponentType<T> }>,
  fallback: React.ReactNode = <div>Loading...</div>,
  errorFallback: React.ReactNode = <div>Error loading component</div>
): ComponentType<T> {
  const LazyComponent = lazy(importFunc);
  
  return function LazyWrapper(props: T) {
    return (
      <LazyErrorBoundary fallback={errorFallback}>
        <Suspense fallback={fallback}>
          <LazyComponent {...props} />
        </Suspense>
      </LazyErrorBoundary>
    );
  };
}

// Preload utility for critical components
export function preloadComponent<T extends object>(
  importFunc: () => Promise<{ default: ComponentType<T> }>
): void {
  importFunc();
}

// Lazy loading with intersection observer
export function useLazyLoad<T extends HTMLElement>(
  threshold: number = 0.1
): [React.RefObject<T>, boolean] {
  const [isVisible, setIsVisible] = React.useState(false);
  const ref = React.useRef<T>(null);

  React.useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect();
        }
      },
      { threshold }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => observer.disconnect();
  }, [threshold]);

  return [ref, isVisible];
} 