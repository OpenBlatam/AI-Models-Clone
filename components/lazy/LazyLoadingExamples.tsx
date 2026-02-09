import React, { Suspense, lazy } from 'react';
import { 
  useIntersectionObserver, 
  useNetworkAwareLazyLoading,
  usePriorityLazyLoading,
  useInteractionLazyLoading,
  usePerformanceAwareLazyLoading,
  useRouteLazyLoading,
  useMemoryAwareLazyLoading
} from './LazyLoadingHooks';

// Example 1: Basic Lazy Loading with Suspense
const LazyComponent = lazy(() => import('../ui/Button'));

export const BasicLazyExample: React.FC = () => {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <LazyComponent />
    </Suspense>
  );
};

// Example 2: Intersection Observer Lazy Loading
export const IntersectionObserverExample: React.FC = () => {
  const { ref, hasIntersected } = useIntersectionObserver();
  
  return (
    <div ref={ref}>
      {hasIntersected ? (
        <Suspense fallback={<div>Loading component...</div>}>
          <LazyComponent />
        </Suspense>
      ) : (
        <div>Component will load when visible</div>
      )}
    </div>
  );
};

// Example 3: Network-Aware Lazy Loading
export const NetworkAwareExample: React.FC = () => {
  const { connectionSpeed, shouldLoadHeavy } = useNetworkAwareLazyLoading();
  
  return (
    <div>
      <div>Connection: {connectionSpeed}</div>
      {shouldLoadHeavy ? (
        <Suspense fallback={<div>Loading heavy component...</div>}>
          <LazyComponent />
        </Suspense>
      ) : (
        <div>Lightweight fallback for slow connections</div>
      )}
    </div>
  );
};

// Example 4: Priority-Based Lazy Loading
export const PriorityBasedExample: React.FC = () => {
  const items = [
    { key: 'critical', priority: 'high' as const, data: 'Critical data' },
    { key: 'important', priority: 'medium' as const, data: 'Important data' },
    { key: 'optional', priority: 'low' as const, data: 'Optional data' }
  ];
  
  const { loadedItems, loadingStates } = usePriorityLazyLoading(items);
  
  return (
    <div>
      {items.map(item => (
        <div key={item.key}>
          <div>{item.key}: {loadingStates[item.key] ? 'Loading...' : loadedItems.has(item.key) ? 'Loaded' : 'Pending'}</div>
        </div>
      ))}
    </div>
  );
};

// Example 5: Interaction-Triggered Lazy Loading
export const InteractionTriggeredExample: React.FC = () => {
  const { loadedFeatures, triggerInteraction } = useInteractionLazyLoading();
  
  return (
    <div>
      <button onClick={() => triggerInteraction('feature1')}>
        Load Feature 1
      </button>
      <button onClick={() => triggerInteraction('feature2')}>
        Load Feature 2
      </button>
      
      {loadedFeatures.has('feature1') && (
        <Suspense fallback={<div>Loading feature 1...</div>}>
          <div>Feature 1 loaded!</div>
        </Suspense>
      )}
      
      {loadedFeatures.has('feature2') && (
        <Suspense fallback={<div>Loading feature 2...</div>}>
          <div>Feature 2 loaded!</div>
        </Suspense>
      )}
    </div>
  );
};

// Example 6: Performance-Aware Lazy Loading
export const PerformanceAwareExample: React.FC = () => {
  const { fps, shouldLoadHeavy } = usePerformanceAwareLazyLoading();
  
  return (
    <div>
      <div>FPS: {fps}</div>
      {shouldLoadHeavy ? (
        <Suspense fallback={<div>Loading heavy component...</div>}>
          <LazyComponent />
        </Suspense>
      ) : (
        <div>Lightweight fallback for low FPS</div>
      )}
    </div>
  );
};

// Example 7: Route-Based Lazy Loading
export const RouteBasedExample: React.FC = () => {
  const { loadedRoutes, loadRoute } = useRouteLazyLoading('/dashboard');
  
  return (
    <div>
      <button onClick={() => loadRoute('/dashboard/analytics')}>
        Load Analytics
      </button>
      <button onClick={() => loadRoute('/dashboard/settings')}>
        Load Settings
      </button>
      
      {loadedRoutes.has('/dashboard/analytics') && (
        <Suspense fallback={<div>Loading analytics...</div>}>
          <div>Analytics loaded!</div>
        </Suspense>
      )}
      
      {loadedRoutes.has('/dashboard/settings') && (
        <Suspense fallback={<div>Loading settings...</div>}>
          <div>Settings loaded!</div>
        </Suspense>
      )}
    </div>
  );
};

// Example 8: Memory-Aware Lazy Loading
export const MemoryAwareExample: React.FC = () => {
  const { memoryUsage, shouldLoadHeavy } = useMemoryAwareLazyLoading();
  
  return (
    <div>
      <div>Memory Usage: {memoryUsage?.toFixed(2)} MB</div>
      {shouldLoadHeavy ? (
        <Suspense fallback={<div>Loading heavy component...</div>}>
          <LazyComponent />
        </Suspense>
      ) : (
        <div>Lightweight fallback for high memory usage</div>
      )}
    </div>
  );
};

// Example 9: Combined Lazy Loading Strategy
export const CombinedLazyExample: React.FC = () => {
  const { connectionSpeed, shouldLoadHeavy: networkOk } = useNetworkAwareLazyLoading();
  const { fps, shouldLoadHeavy: performanceOk } = usePerformanceAwareLazyLoading();
  const { memoryUsage, shouldLoadHeavy: memoryOk } = useMemoryAwareLazyLoading();
  const { ref, hasIntersected } = useIntersectionObserver();
  
  const shouldLoad = networkOk && performanceOk && memoryOk && hasIntersected;
  
  return (
    <div ref={ref}>
      <div>Network: {connectionSpeed}</div>
      <div>FPS: {fps}</div>
      <div>Memory: {memoryUsage?.toFixed(2)} MB</div>
      
      {shouldLoad ? (
        <Suspense fallback={<div>Loading optimized component...</div>}>
          <LazyComponent />
        </Suspense>
      ) : (
        <div>Component will load when all conditions are met</div>
      )}
    </div>
  );
};

// Example 10: Lazy Loading with Error Boundaries
export const LazyWithErrorBoundaryExample: React.FC = () => {
  const [hasError, setHasError] = React.useState(false);
  
  if (hasError) {
    return <div>Something went wrong. <button onClick={() => setHasError(false)}>Retry</button></div>;
  }
  
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <ErrorBoundary onError={() => setHasError(true)}>
        <LazyComponent />
      </ErrorBoundary>
    </Suspense>
  );
};

// Error Boundary Component
class ErrorBoundary extends React.Component<
  { children: React.ReactNode; onError: () => void },
  { hasError: boolean }
> {
  constructor(props: { children: React.ReactNode; onError: () => void }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(): { hasError: boolean } {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    console.error('Lazy component error:', error, errorInfo);
    this.props.onError();
  }

  render(): React.ReactNode {
    if (this.state.hasError) {
      return <div>Error loading component</div>;
    }

    return this.props.children;
  }
} 