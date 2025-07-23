# Lazy Loading Implementation Guide

## Overview

This implementation provides comprehensive code splitting and lazy loading for non-critical components using React's Suspense and dynamic imports. The solution includes patterns for both web (Next.js) and React Native applications.

## Key Features

- **Code Splitting**: Automatic chunk creation for better performance
- **Error Boundaries**: Graceful error handling for failed component loads
- **Loading States**: Customizable loading indicators
- **Retry Mechanism**: Automatic retry for failed imports
- **Performance Monitoring**: Load time tracking and optimization
- **Conditional Loading**: Role-based and feature-flag based loading
- **Preloading**: Hover/press-based preloading for better UX

## Implementation Patterns

### 1. Basic Lazy Loading

```tsx
import React, { Suspense, lazy } from 'react';

const AnalyticsDashboard = lazy(() => import('./analytics/AnalyticsDashboard'));

function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <AnalyticsDashboard />
    </Suspense>
  );
}
```

### 2. Error Boundary Pattern

```tsx
const ErrorBoundary = ({ children, fallback }) => {
  const [hasError, setHasError] = React.useState(false);

  if (hasError) {
    return fallback || <div>Error loading component</div>;
  }

  return <>{children}</>;
};

// Usage
<Suspense fallback={<LoadingSpinner />}>
  <ErrorBoundary fallback={<ErrorComponent />}>
    <LazyComponent />
  </ErrorBoundary>
</Suspense>
```

### 3. Retry Mechanism

```tsx
const retryImport = (importFn, retries = 3) => {
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

const ComponentWithRetry = lazy(() => 
  retryImport(() => import('./Component'))
);
```

### 4. Conditional Loading

```tsx
const ConditionalComponent = ({ userRole }) => {
  const AdminComponent = lazy(() => import('./admin/AdminPanel'));
  const UserComponent = lazy(() => import('./user/UserPanel'));

  return (
    <Suspense fallback={<LoadingSpinner />}>
      {userRole === 'admin' ? <AdminComponent /> : <UserComponent />}
    </Suspense>
  );
};
```

### 5. Preloading Pattern

```tsx
const PreloadComponent = () => {
  const [isPreloaded, setIsPreloaded] = React.useState(false);
  const [isVisible, setIsVisible] = React.useState(false);

  const handleMouseEnter = () => {
    if (!isPreloaded) setIsPreloaded(true);
  };

  const handleClick = () => setIsVisible(true);

  return (
    <div>
      <button onMouseEnter={handleMouseEnter} onClick={handleClick}>
        Load Component
      </button>
      
      {isVisible && isPreloaded && (
        <Suspense fallback={<LoadingSpinner />}>
          <LazyComponent />
        </Suspense>
      )}
    </div>
  );
};
```

## Next.js Specific Implementation

### Dynamic Imports

```tsx
import dynamic from 'next/dynamic';

const AnalyticsDashboard = dynamic(
  () => import('../components/analytics/AnalyticsDashboard'),
  {
    loading: () => <div className="animate-pulse h-32 bg-gray-200 rounded"></div>,
    ssr: false, // Disable SSR for client-only components
    suspense: true
  }
);
```

### Webpack Configuration

```js
// next.config.js
module.exports = {
  webpack: (config) => {
    config.optimization.splitChunks = {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
          priority: 10,
        },
        analytics: {
          test: /[\\/]components[\\/]analytics[\\/]/,
          name: 'analytics',
          chunks: 'all',
          priority: 20,
        },
      },
    };
    return config;
  },
};
```

## React Native Implementation

### Basic Pattern

```tsx
import React, { Suspense, lazy } from 'react';
import { View, ActivityIndicator } from 'react-native';

const AnalyticsChart = lazy(() => import('./analytics/AnalyticsChart'));

const LoadingSpinner = () => (
  <View style={styles.loadingContainer}>
    <ActivityIndicator size="large" color="#007AFF" />
  </View>
);

function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <AnalyticsChart />
    </Suspense>
  );
}
```

### FlatList Optimization

```tsx
const LazyLoadingFlatList = () => {
  const renderItem = ({ item, index }) => (
    <Suspense key={index} fallback={<LoadingSpinner />}>
      <LazyItemComponent item={item} />
    </Suspense>
  );

  return (
    <FlatList
      data={items}
      renderItem={renderItem}
      removeClippedSubviews={true}
      maxToRenderPerBatch={10}
      windowSize={10}
      initialNumToRender={5}
    />
  );
};
```

## Performance Optimization

### 1. Bundle Analysis

```bash
# Analyze bundle size
npm run build
npx @next/bundle-analyzer

# For React Native
npx react-native bundle --platform ios --dev false --entry-file index.js --bundle-output ios-release.bundle --sourcemap-output ios-release.bundle.map
```

### 2. Performance Monitoring

```tsx
const PerformanceMonitoredComponent = lazy(async () => {
  const startTime = performance.now();
  
  try {
    const module = await import('./Component');
    const loadTime = performance.now() - startTime;
    console.log(`Component loaded in ${loadTime.toFixed(2)}ms`);
    return module;
  } catch (error) {
    const loadTime = performance.now() - startTime;
    console.error(`Component failed after ${loadTime.toFixed(2)}ms:`, error);
    throw error;
  }
});
```

### 3. Caching Strategy

```js
// Service Worker for caching
const CACHE_NAME = 'lazy-components-v1';

self.addEventListener('fetch', (event) => {
  if (event.request.url.includes('/_next/static/chunks/')) {
    event.respondWith(
      caches.open(CACHE_NAME).then((cache) => {
        return cache.match(event.request).then((response) => {
          return response || fetch(event.request).then((response) => {
            cache.put(event.request, response.clone());
            return response;
          });
        });
      })
    );
  }
});
```

## Best Practices

### 1. Component Organization

```
components/
├── critical/
│   ├── Header.tsx
│   ├── Navigation.tsx
│   └── Footer.tsx
├── lazy/
│   ├── analytics/
│   │   └── AnalyticsDashboard.tsx
│   ├── admin/
│   │   └── AdminPanel.tsx
│   └── user/
│       └── UserProfile.tsx
└── shared/
    ├── LoadingSpinner.tsx
    └── ErrorBoundary.tsx
```

### 2. Loading State Design

```tsx
const LoadingSpinner = ({ size = 'md' }) => {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12'
  };

  return (
    <div className={`animate-spin rounded-full border-b-2 border-blue-600 ${sizeClasses[size]}`}></div>
  );
};
```

### 3. Error Handling

```tsx
const ErrorFallback = ({ error, resetErrorBoundary }) => (
  <div className="p-4 bg-red-50 border border-red-200 rounded-md">
    <p className="text-red-600">Something went wrong</p>
    <button onClick={resetErrorBoundary} className="mt-2 px-3 py-1 bg-red-500 text-white rounded">
      Try again
    </button>
  </div>
);
```

### 4. Testing

```tsx
// Test lazy loading
import { render, waitFor } from '@testing-library/react';

test('lazy loads component', async () => {
  const { getByText } = render(
    <Suspense fallback={<div>Loading...</div>}>
      <LazyComponent />
    </Suspense>
  );

  await waitFor(() => {
    expect(getByText('Component Content')).toBeInTheDocument();
  });
});
```

## Monitoring and Analytics

### 1. Performance Metrics

```tsx
// Track component load times
const trackComponentLoad = (componentName: string, loadTime: number) => {
  analytics.track('component_loaded', {
    component: componentName,
    loadTime,
    timestamp: Date.now()
  });
};
```

### 2. Error Tracking

```tsx
// Track lazy loading errors
const trackLazyLoadError = (componentName: string, error: Error) => {
  analytics.track('lazy_load_error', {
    component: componentName,
    error: error.message,
    stack: error.stack
  });
};
```

## Conclusion

This lazy loading implementation provides:

- **Improved Performance**: Reduced initial bundle size and faster page loads
- **Better UX**: Smooth loading states and error handling
- **Scalability**: Easy to add new lazy-loaded components
- **Maintainability**: Clear patterns and best practices
- **Monitoring**: Performance tracking and error reporting

The implementation follows React best practices and provides patterns for both web and React Native applications, ensuring optimal performance across all platforms. 