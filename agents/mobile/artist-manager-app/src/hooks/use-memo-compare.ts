import { useRef, useEffect } from 'react';

/**
 * Hook for memoizing values with custom comparison function
 */
export function useMemoCompare<T>(value: T, compare: (prev: T, next: T) => boolean): T {
  const ref = useRef<T>(value);

  useEffect(() => {
    if (!compare(ref.current, value)) {
      ref.current = value;
    }
  }, [value, compare]);

  return ref.current;
}


