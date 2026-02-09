import { useState, useCallback, useRef } from 'react';

/**
 * Hook for state with undo/redo functionality
 */
export function useStateWithHistory<T>(initialValue: T, maxHistory = 50) {
  const [currentValue, setCurrentValue] = useState<T>(initialValue);
  const historyRef = useRef<T[]>([initialValue]);
  const currentIndexRef = useRef(0);

  const setValue = useCallback(
    (value: T | ((prev: T) => T)) => {
      const newValue = typeof value === 'function' ? (value as (prev: T) => T)(currentValue) : value;
      
      // Remove any future history if we're not at the end
      if (currentIndexRef.current < historyRef.current.length - 1) {
        historyRef.current = historyRef.current.slice(0, currentIndexRef.current + 1);
      }

      // Add new value to history
      historyRef.current.push(newValue);

      // Limit history size
      if (historyRef.current.length > maxHistory) {
        historyRef.current.shift();
      } else {
        currentIndexRef.current++;
      }

      setCurrentValue(newValue);
    },
    [currentValue, maxHistory]
  );

  const undo = useCallback(() => {
    if (currentIndexRef.current > 0) {
      currentIndexRef.current--;
      setCurrentValue(historyRef.current[currentIndexRef.current]);
    }
  }, []);

  const redo = useCallback(() => {
    if (currentIndexRef.current < historyRef.current.length - 1) {
      currentIndexRef.current++;
      setCurrentValue(historyRef.current[currentIndexRef.current]);
    }
  }, []);

  const canUndo = currentIndexRef.current > 0;
  const canRedo = currentIndexRef.current < historyRef.current.length - 1;

  return {
    value: currentValue,
    setValue,
    undo,
    redo,
    canUndo,
    canRedo,
    history: historyRef.current,
  };
}

