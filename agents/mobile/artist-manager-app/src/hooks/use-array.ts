import { useState, useCallback } from 'react';

/**
 * Hook for array state with common operations
 */
export function useArray<T>(initialArray: T[] = []) {
  const [array, setArray] = useState<T[]>(initialArray);

  const push = useCallback((item: T) => {
    setArray((prev) => [...prev, item]);
  }, []);

  const pop = useCallback(() => {
    setArray((prev) => {
      const newArray = [...prev];
      newArray.pop();
      return newArray;
    });
  }, []);

  const unshift = useCallback((item: T) => {
    setArray((prev) => [item, ...prev]);
  }, []);

  const shift = useCallback(() => {
    setArray((prev) => {
      const newArray = [...prev];
      newArray.shift();
      return newArray;
    });
  }, []);

  const remove = useCallback((index: number) => {
    setArray((prev) => prev.filter((_, i) => i !== index));
  }, []);

  const update = useCallback((index: number, item: T) => {
    setArray((prev) => {
      const newArray = [...prev];
      newArray[index] = item;
      return newArray;
    });
  }, []);

  const clear = useCallback(() => {
    setArray([]);
  }, []);

  const set = useCallback((newArray: T[] | ((prev: T[]) => T[])) => {
    setArray(newArray);
  }, []);

  return {
    array,
    set,
    push,
    pop,
    unshift,
    shift,
    remove,
    update,
    clear,
    length: array.length,
    isEmpty: array.length === 0,
  };
}

