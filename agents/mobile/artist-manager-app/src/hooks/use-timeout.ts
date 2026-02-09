import { useEffect, useRef } from 'react';

/**
 * Hook for running a function after a delay
 */
export function useTimeout(callback: () => void, delay: number | null) {
  const savedCallback = useRef<() => void>();

  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  useEffect(() => {
    if (delay !== null) {
      const id = setTimeout(() => {
        savedCallback.current?.();
      }, delay);
      return () => clearTimeout(id);
    }
  }, [delay]);
}


