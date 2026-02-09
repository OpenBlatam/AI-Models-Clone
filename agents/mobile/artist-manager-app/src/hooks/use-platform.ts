import { Platform } from 'react-native';

/**
 * Hook for platform-specific logic
 */
export function usePlatform() {
  return {
    isIOS: Platform.OS === 'ios',
    isAndroid: Platform.OS === 'android',
    isWeb: Platform.OS === 'web',
    platform: Platform.OS,
    version: Platform.Version,
    select: Platform.select,
  };
}


