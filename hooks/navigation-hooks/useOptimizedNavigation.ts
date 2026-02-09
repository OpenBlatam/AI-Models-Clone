import { useCallback, useMemo, useRef } from 'react';
import { useRouter, usePathname } from 'expo-router';

interface NavigationState {
  currentRoute: string;
  previousRoute: string | null;
  navigationHistory: string[];
}

interface UseOptimizedNavigationReturn {
  navigate: (route: string, params?: Record<string, any>) => void;
  goBack: () => void;
  canGoBack: boolean;
  currentRoute: string;
  navigationHistory: string[];
  resetNavigation: () => void;
}

export const useOptimizedNavigation = (): UseOptimizedNavigationReturn => {
  const router = useRouter();
  const pathname = usePathname();
  const navigationRef = useRef<NavigationState>({
    currentRoute: pathname,
    previousRoute: null,
    navigationHistory: [pathname],
  });

  const navigate = useCallback((route: string, params?: Record<string, any>) => {
    const currentRoute = navigationRef.current.currentRoute;
    
    navigationRef.current = {
      currentRoute: route,
      previousRoute: currentRoute,
      navigationHistory: [...navigationRef.current.navigationHistory, route],
    };

    if (params) {
      router.push({ pathname: route, params });
    } else {
      router.push(route);
    }
  }, [router]);

  const goBack = useCallback(() => {
    const { navigationHistory } = navigationRef.current;
    if (navigationHistory.length > 1) {
      const previousRoute = navigationHistory[navigationHistory.length - 2];
      navigationRef.current.navigationHistory = navigationHistory.slice(0, -1);
      navigationRef.current.currentRoute = previousRoute;
      navigationRef.current.previousRoute = navigationHistory[navigationHistory.length - 1];
      router.back();
    }
  }, [router]);

  const canGoBack = useMemo(() => {
    return navigationRef.current.navigationHistory.length > 1;
  }, [navigationRef.current.navigationHistory.length]);

  const resetNavigation = useCallback(() => {
    navigationRef.current = {
      currentRoute: pathname,
      previousRoute: null,
      navigationHistory: [pathname],
    };
  }, [pathname]);

  return {
    navigate,
    goBack,
    canGoBack,
    currentRoute: navigationRef.current.currentRoute,
    navigationHistory: navigationRef.current.navigationHistory,
    resetNavigation,
  };
}; 