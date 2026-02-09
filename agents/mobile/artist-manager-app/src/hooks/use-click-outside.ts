import { useRef, RefObject } from 'react';
import { View, Pressable } from 'react-native';

/**
 * Hook for detecting presses outside an element (React Native version)
 * Returns a ref and a handler to attach to a Pressable wrapper
 */
export function useClickOutside<T extends View>(
  handler: () => void,
  enabled = true
): { ref: RefObject<T>; onPressOut: () => void } {
  const ref = useRef<T>(null);

  const onPressOut = () => {
    if (enabled) {
      handler();
    }
  };

  return { ref, onPressOut };
}

