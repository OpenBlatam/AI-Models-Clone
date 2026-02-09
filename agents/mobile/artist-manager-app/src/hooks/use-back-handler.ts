import { useEffect } from 'react';
import { BackHandler } from 'react-native';

/**
 * Hook for handling Android back button
 */
export function useBackHandler(handler: () => boolean) {
  useEffect(() => {
    const backHandler = BackHandler.addEventListener('hardwareBackPress', () => {
      return handler();
    });

    return () => backHandler.remove();
  }, [handler]);
}

