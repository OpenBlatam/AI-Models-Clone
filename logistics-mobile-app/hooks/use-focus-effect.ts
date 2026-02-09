import React, { useCallback } from 'react';
import { useFocusEffect as useRNFocusEffect } from 'expo-router';

export function useFocusEffect(callback: () => void | (() => void), deps: React.DependencyList = []) {
  useRNFocusEffect(
    useCallback(() => {
      const cleanup = callback();
      return cleanup;
    }, deps)
  );
}
