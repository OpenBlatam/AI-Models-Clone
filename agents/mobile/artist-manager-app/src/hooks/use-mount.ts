import { useEffect, useRef } from 'react';

/**
 * Hook that runs a function only on mount
 */
export function useMount(fn: () => void | (() => void)) {
  const hasMountedRef = useRef(false);

  useEffect(() => {
    if (!hasMountedRef.current) {
      hasMountedRef.current = true;
      return fn();
    }
  }, [fn]);
}


