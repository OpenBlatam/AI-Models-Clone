import { useEffect, useRef } from 'react';

/**
 * Hook that runs a function only on unmount
 */
export function useUnmount(fn: () => void) {
  const fnRef = useRef(fn);

  useEffect(() => {
    fnRef.current = fn;
  }, [fn]);

  useEffect(() => {
    return () => {
      fnRef.current();
    };
  }, []);
}


