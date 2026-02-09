import { useState, useCallback } from 'react';

/**
 * Hook for stack data structure
 */
export function useStack<T>(initialStack: T[] = []) {
  const [stack, setStack] = useState<T[]>(initialStack);

  const push = useCallback((item: T) => {
    setStack((prev) => [...prev, item]);
  }, []);

  const pop = useCallback(() => {
    let item: T | undefined;
    setStack((prev) => {
      const newStack = [...prev];
      item = newStack.pop();
      return newStack;
    });
    return item;
  }, []);

  const peek = useCallback(() => {
    return stack[stack.length - 1];
  }, [stack]);

  const clear = useCallback(() => {
    setStack([]);
  }, []);

  return {
    stack,
    push,
    pop,
    peek,
    clear,
    length: stack.length,
    isEmpty: stack.length === 0,
  };
}

