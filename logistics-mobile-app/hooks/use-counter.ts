import { useState, useCallback } from 'react';
import { UseCounterReturn } from '@/types';

export function useCounter(initialValue: number = 0, min?: number, max?: number): UseCounterReturn {
  const [count, setCount] = useState(initialValue);

  const increment = useCallback(() => {
    setCount((prev) => {
      const next = prev + 1;
      if (max !== undefined && next > max) return prev;
      return next;
    });
  }, [max]);

  const decrement = useCallback(() => {
    setCount((prev) => {
      const next = prev - 1;
      if (min !== undefined && next < min) return prev;
      return next;
    });
  }, [min]);

  const reset = useCallback(() => {
    setCount(initialValue);
  }, [initialValue]);

  const setCountValue = useCallback(
    (value: number) => {
      let newValue = value;
      if (min !== undefined && newValue < min) newValue = min;
      if (max !== undefined && newValue > max) newValue = max;
      setCount(newValue);
    },
    [min, max]
  );

  return {
    count,
    increment,
    decrement,
    reset,
    setCount: setCountValue,
  };
}

