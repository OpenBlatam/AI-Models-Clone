import { useState, useCallback } from 'react';

/**
 * Hook for queue data structure
 */
export function useQueue<T>(initialQueue: T[] = []) {
  const [queue, setQueue] = useState<T[]>(initialQueue);

  const enqueue = useCallback((item: T) => {
    setQueue((prev) => [...prev, item]);
  }, []);

  const dequeue = useCallback(() => {
    let item: T | undefined;
    setQueue((prev) => {
      const newQueue = [...prev];
      item = newQueue.shift();
      return newQueue;
    });
    return item;
  }, []);

  const peek = useCallback(() => {
    return queue[0];
  }, [queue]);

  const clear = useCallback(() => {
    setQueue([]);
  }, []);

  return {
    queue,
    enqueue,
    dequeue,
    peek,
    clear,
    length: queue.length,
    isEmpty: queue.length === 0,
  };
}

