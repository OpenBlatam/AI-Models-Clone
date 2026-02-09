import { useEffect } from 'react';
import { Platform } from 'react-native';

/**
 * Hook to lock body scroll (mainly for web/modal scenarios)
 */
export function useLockBodyScroll(locked = true) {
  useEffect(() => {
    if (Platform.OS !== 'web' || !locked) {
      return;
    }

    const originalStyle = window.getComputedStyle(document.body).overflow;
    document.body.style.overflow = 'hidden';

    return () => {
      document.body.style.overflow = originalStyle;
    };
  }, [locked]);
}

