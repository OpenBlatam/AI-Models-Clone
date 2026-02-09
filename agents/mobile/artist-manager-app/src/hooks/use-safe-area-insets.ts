import { useSafeAreaInsets as useRNSafeAreaInsets } from 'react-native-safe-area-context';

/**
 * Hook for getting safe area insets
 */
export function useSafeAreaInsets() {
  return useRNSafeAreaInsets();
}

