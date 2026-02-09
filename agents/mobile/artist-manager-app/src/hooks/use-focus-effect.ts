import { useCallback } from 'react';
import { useFocusEffect as useRNFocusEffect } from '@react-navigation/native';

/**
 * Hook that runs an effect when the screen comes into focus
 * Uses React Navigation's useFocusEffect
 */
export function useFocusEffect(callback: () => void | (() => void)) {
  const stableCallback = useCallback(callback, [callback]);

  useRNFocusEffect(stableCallback);
}

