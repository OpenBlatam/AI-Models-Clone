import { useState, useEffect, useRef } from 'react';
import { AppState, AppStateStatus } from 'react-native';

export function useAppState() {
  const [appState, setAppState] = useState<AppStateStatus>(AppState.currentState);
  const [isActive, setIsActive] = useState(true);
  const appStateRef = useRef<AppStateStatus>(AppState.currentState);

  useEffect(() => {
    function handleAppStateChange(nextAppState: AppStateStatus) {
      const previousAppState = appStateRef.current;
      appStateRef.current = nextAppState;
      setAppState(nextAppState);
      setIsActive(nextAppState === 'active');

      if (previousAppState.match(/inactive|background/) && nextAppState === 'active') {
        // App came to foreground
      } else if (previousAppState === 'active' && nextAppState.match(/inactive|background/)) {
        // App went to background
      }
    }

    const subscription = AppState.addEventListener('change', handleAppStateChange);

    return () => {
      subscription.remove();
    };
  }, []);

  return {
    appState,
    isActive,
    isBackground: appState === 'background',
    isInactive: appState === 'inactive',
  };
}


