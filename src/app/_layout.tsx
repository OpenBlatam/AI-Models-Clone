import React from 'react';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { AppProvider } from '../store/app-store';
import { ErrorBoundary } from '../components/error-boundary/error-boundary';
import { useTheme } from '../store/app-store';
import MasterNavigation from '../components/navigation/master-navigation';

// ============================================================================
// ROOT LAYOUT COMPONENT
// ============================================================================

function RootLayoutContent(): JSX.Element {
  const { effectiveTheme } = useTheme();

  return (
    <>
      <StatusBar style={effectiveTheme === 'dark' ? 'light' : 'dark'} />
      <MasterNavigation />
    </>
  );
}

export default function RootLayout(): JSX.Element {
  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <SafeAreaProvider>
        <AppProvider>
          <ErrorBoundary>
            <RootLayoutContent />
          </ErrorBoundary>
        </AppProvider>
      </SafeAreaProvider>
    </GestureHandlerRootView>
  );
}