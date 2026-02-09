import React, { Suspense, lazy } from 'react';
import { View, Text, ActivityIndicator, StyleSheet, FlatList, TouchableOpacity } from 'react-native';

// Lazy load non-critical React Native components
const AnalyticsChart = lazy(() => import('./analytics/AnalyticsChart'));
const UserProfileCard = lazy(() => import('./user/UserProfileCard'));
const SettingsForm = lazy(() => import('./settings/SettingsForm'));
const NotificationList = lazy(() => import('./notifications/NotificationList'));
const ChatInterface = lazy(() => import('./chat/ChatInterface'));
const FileUploadComponent = lazy(() => import('./upload/FileUploadComponent'));
const DataTable = lazy(() => import('./data/DataTable'));
const AdminDashboard = lazy(() => import('./admin/AdminDashboard'));

// Loading fallback components for React Native
const LoadingSpinner = () => (
  <View style={styles.loadingContainer}>
    <ActivityIndicator size="large" color="#007AFF" />
    <Text style={styles.loadingText}>Loading...</Text>
  </View>
);

const ErrorFallback = ({ error }: { error: Error }) => (
  <View style={styles.errorContainer}>
    <Text style={styles.errorText}>Error loading component</Text>
    <Text style={styles.errorDetails}>{error.message}</Text>
  </View>
);

// Error boundary for React Native
class ErrorBoundary extends React.Component<
  { children: React.ReactNode; fallback?: React.ComponentType<any> },
  { hasError: boolean; error: Error | null }
> {
  constructor(props: { children: React.ReactNode; fallback?: React.ComponentType<any> }) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Lazy loading error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback ? (
        <this.props.fallback error={this.state.error!} />
      ) : (
        <ErrorFallback error={this.state.error!} />
      );
    }

    return this.props.children;
  }
}

// Main component with lazy loading for React Native
export function DashboardWithLazyLoading() {
  return (
    <View style={styles.container}>
      {/* Critical components loaded immediately */}
      <View style={styles.criticalSection}>
        <Text style={styles.sectionTitle}>Quick Actions</Text>
        {/* Critical content */}
      </View>

      {/* Non-critical components with lazy loading */}
      <Suspense fallback={<LoadingSpinner />}>
        <ErrorBoundary>
          <AnalyticsChart />
        </ErrorBoundary>
      </Suspense>

      <Suspense fallback={<LoadingSpinner />}>
        <ErrorBoundary>
          <UserProfileCard />
        </ErrorBoundary>
      </Suspense>

      <Suspense fallback={<LoadingSpinner />}>
        <ErrorBoundary>
          <SettingsForm />
        </ErrorBoundary>
      </Suspense>

      <Suspense fallback={<LoadingSpinner />}>
        <ErrorBoundary>
          <NotificationList />
        </ErrorBoundary>
      </Suspense>

      <Suspense fallback={<LoadingSpinner />}>
        <ErrorBoundary>
          <ChatInterface />
        </ErrorBoundary>
      </Suspense>

      <Suspense fallback={<LoadingSpinner />}>
        <ErrorBoundary>
          <FileUploadComponent />
        </ErrorBoundary>
      </Suspense>

      <Suspense fallback={<LoadingSpinner />}>
        <ErrorBoundary>
          <DataTable />
        </ErrorBoundary>
      </Suspense>

      <Suspense fallback={<LoadingSpinner />}>
        <ErrorBoundary>
          <AdminDashboard />
        </ErrorBoundary>
      </Suspense>
    </View>
  );
}

// Lazy loading with FlatList optimization
export function LazyLoadingFlatList() {
  const [items, setItems] = React.useState<Array<any>>([]);
  const [loading, setLoading] = React.useState(false);

  const loadMoreItems = async () => {
    setLoading(true);
    // Simulate API call
    const newItems = await fetch('/api/items');
    setItems(prev => [...prev, ...newItems]);
    setLoading(false);
  };

  const renderItem = ({ item, index }: { item: any; index: number }) => (
    <Suspense key={index} fallback={<LoadingSpinner />}>
      <LazyItemComponent item={item} />
    </Suspense>
  );

  return (
    <FlatList
      data={items}
      renderItem={renderItem}
      keyExtractor={(item, index) => index.toString()}
      onEndReached={loadMoreItems}
      onEndReachedThreshold={0.1}
      ListFooterComponent={loading ? <LoadingSpinner /> : null}
      removeClippedSubviews={true}
      maxToRenderPerBatch={10}
      windowSize={10}
      initialNumToRender={5}
    />
  );
}

// Lazy loading with conditional rendering based on user role
export function ConditionalLazyLoading({ userRole }: { userRole: string }) {
  const AdminComponent = lazy(() => import('./admin/AdminDashboard'));
  const UserComponent = lazy(() => import('./user/UserDashboard'));

  return (
    <View style={styles.container}>
      {userRole === 'admin' ? (
        <Suspense fallback={<LoadingSpinner />}>
          <ErrorBoundary>
            <AdminComponent />
          </ErrorBoundary>
        </Suspense>
      ) : (
        <Suspense fallback={<LoadingSpinner />}>
          <ErrorBoundary>
            <UserComponent />
          </ErrorBoundary>
        </Suspense>
      )}
    </View>
  );
}

// Lazy loading with preloading on press
export function PreloadOnPressLazyLoading() {
  const [isPreloaded, setIsPreloaded] = React.useState(false);
  const [isVisible, setIsVisible] = React.useState(false);

  const handlePressIn = () => {
    if (!isPreloaded) {
      setIsPreloaded(true);
    }
  };

  const handlePress = () => {
    setIsVisible(true);
  };

  return (
    <View style={styles.container}>
      <TouchableOpacity
        onPressIn={handlePressIn}
        onPress={handlePress}
        style={styles.button}
      >
        <Text style={styles.buttonText}>Load Analytics</Text>
      </TouchableOpacity>

      {isVisible && isPreloaded && (
        <Suspense fallback={<LoadingSpinner />}>
          <ErrorBoundary>
            <AnalyticsChart />
          </ErrorBoundary>
        </Suspense>
      )}
    </View>
  );
}

// Lazy loading with retry mechanism
export function LazyLoadingWithRetry() {
  const [retryCount, setRetryCount] = React.useState(0);
  const maxRetries = 3;

  const retryImport = (importFn: () => Promise<any>) => {
    return new Promise((resolve, reject) => {
      importFn()
        .then(resolve)
        .catch((error) => {
          if (retryCount < maxRetries) {
            setTimeout(() => {
              setRetryCount(prev => prev + 1);
              retryImport(importFn).then(resolve).catch(reject);
            }, 1000);
          } else {
            reject(error);
          }
        });
    });
  };

  const AnalyticsWithRetry = lazy(() => 
    retryImport(() => import('./analytics/AnalyticsChart'))
  );

  return (
    <Suspense fallback={<LoadingSpinner />}>
      <ErrorBoundary>
        <AnalyticsWithRetry />
      </ErrorBoundary>
    </Suspense>
  );
}

// Lazy loading with performance monitoring
export function PerformanceMonitoredLazyLoading() {
  const [loadTime, setLoadTime] = React.useState<number | null>(null);

  const MonitoredAnalytics = lazy(async () => {
    const startTime = Date.now();
    
    try {
      const module = await import('./analytics/AnalyticsChart');
      const endTime = Date.now();
      setLoadTime(endTime - startTime);
      
      console.log(`AnalyticsChart loaded in ${endTime - startTime}ms`);
      return module;
    } catch (error) {
      const endTime = Date.now();
      console.error(`AnalyticsChart failed to load after ${endTime - startTime}ms:`, error);
      throw error;
    }
  });

  return (
    <View style={styles.container}>
      {loadTime && (
        <Text style={styles.performanceText}>
          Loaded in {loadTime}ms
        </Text>
      )}
      
      <Suspense fallback={<LoadingSpinner />}>
        <ErrorBoundary>
          <MonitoredAnalytics />
        </ErrorBoundary>
      </Suspense>
    </View>
  );
}

// Styles
const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
  errorContainer: {
    padding: 20,
    backgroundColor: '#ffebee',
    borderRadius: 8,
    margin: 10,
  },
  errorText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#d32f2f',
  },
  errorDetails: {
    fontSize: 14,
    color: '#666',
    marginTop: 5,
  },
  criticalSection: {
    padding: 16,
    backgroundColor: '#f5f5f5',
    borderRadius: 8,
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  button: {
    backgroundColor: '#007AFF',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 16,
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  performanceText: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
    marginBottom: 10,
  },
});

// Export all components
export {
  AnalyticsChart,
  UserProfileCard,
  SettingsForm,
  NotificationList,
  ChatInterface,
  FileUploadComponent,
  DataTable,
  AdminDashboard,
  LoadingSpinner,
  ErrorFallback,
  ErrorBoundary
}; 