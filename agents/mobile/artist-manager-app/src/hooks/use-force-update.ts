import { useState, useCallback } from 'react';

/**
 * Hook for forcing component re-render
 */
export function useForceUpdate() {
  const [, setTick] = useState(0);

  const update = useCallback(() => {
    setTick((tick) => tick + 1);
  }, []);

  return update;
}


