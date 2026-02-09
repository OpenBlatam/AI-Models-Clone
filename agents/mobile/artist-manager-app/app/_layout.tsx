import { useEffect } from 'react';
import { Stack } from 'expo-router';
import * as SplashScreen from 'expo-splash-screen';
import * as Font from 'expo-font';
import { QueryClient } from '@tanstack/react-query';
import { AppProvider } from '@/providers';

SplashScreen.preventAutoHideAsync();

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      gcTime: 1000 * 60 * 10, // 10 minutes (formerly cacheTime)
      retry: 2,
      refetchOnWindowFocus: false,
      networkMode: 'online',
    },
    mutations: {
      retry: 1,
      networkMode: 'online',
    },
  },
});

async function loadResourcesAsync() {
  try {
    // Load fonts if needed
    await Font.loadAsync({
      // Add custom fonts here if needed
      // 'custom-font': require('./assets/fonts/CustomFont.ttf'),
    });
  } catch (e) {
    console.warn('Error loading resources:', e);
  }
}

function RootLayoutNav() {
  useEffect(() => {
    async function prepare() {
      try {
        await loadResourcesAsync();
        // Small delay to ensure smooth transition
        await new Promise((resolve) => setTimeout(resolve, 500));
      } catch (e) {
        console.warn('Error preparing app:', e);
      } finally {
        await SplashScreen.hideAsync();
      }
    }

    prepare();
  }, []);

  return (
    <AppProvider queryClient={queryClient}>
      <Stack
        screenOptions={{
          headerShown: false,
          animation: 'slide_from_right',
        }}
      >
        <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
        <Stack.Screen name="auth" options={{ headerShown: false }} />
      </Stack>
    </AppProvider>
  );
}

export default function RootLayout() {
  return <RootLayoutNav />;
}

