import { ReactNode } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';
import { ErrorBoundary, NetworkStatus, ToastProvider } from '@/components';
import { ThemeProvider, useTheme } from '@/context';

interface AppProviderProps {
  children: ReactNode;
  queryClient: QueryClient;
}

function AppContent({ children }: { children: ReactNode }) {
  const { isDark } = useTheme();

  return (
    <>
      <StatusBar style={isDark ? 'light' : 'dark'} />
      <NetworkStatus />
      {children}
    </>
  );
}

export function AppProvider({ children, queryClient }: AppProviderProps) {
  return (
    <ErrorBoundary>
      <GestureHandlerRootView style={{ flex: 1 }}>
        <SafeAreaProvider>
          <QueryClientProvider client={queryClient}>
            <ThemeProvider>
              <ToastProvider>
                <AppContent>{children}</AppContent>
              </ToastProvider>
            </ThemeProvider>
          </QueryClientProvider>
        </SafeAreaProvider>
      </GestureHandlerRootView>
    </ErrorBoundary>
  );
}

