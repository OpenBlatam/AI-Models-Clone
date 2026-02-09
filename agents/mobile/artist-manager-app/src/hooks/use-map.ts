import { useState, useCallback } from 'react';

/**
 * Hook for Map-like state with common operations
 */
export function useMap<K, V>(initialMap: Map<K, V> | [K, V][] = []) {
  const [map, setMap] = useState<Map<K, V>>(new Map(initialMap));

  const set = useCallback((key: K, value: V) => {
    setMap((prev) => {
      const newMap = new Map(prev);
      newMap.set(key, value);
      return newMap;
    });
  }, []);

  const get = useCallback(
    (key: K) => {
      return map.get(key);
    },
    [map]
  );

  const remove = useCallback((key: K) => {
    setMap((prev) => {
      const newMap = new Map(prev);
      newMap.delete(key);
      return newMap;
    });
  }, []);

  const has = useCallback(
    (key: K) => {
      return map.has(key);
    },
    [map]
  );

  const clear = useCallback(() => {
    setMap(new Map());
  }, []);

  const setAll = useCallback((newMap: Map<K, V> | [K, V][]) => {
    setMap(new Map(newMap));
  }, []);

  return {
    map,
    set,
    get,
    remove,
    has,
    clear,
    setAll,
    size: map.size,
    isEmpty: map.size === 0,
    keys: Array.from(map.keys()),
    values: Array.from(map.values()),
    entries: Array.from(map.entries()),
  };
}

