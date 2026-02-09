import { useIsFocused as useRNIsFocused } from '@react-navigation/native';

/**
 * Hook that returns whether the screen is currently focused
 * Uses React Navigation's useIsFocused
 */
export function useIsFocused(): boolean {
  return useRNIsFocused();
}

