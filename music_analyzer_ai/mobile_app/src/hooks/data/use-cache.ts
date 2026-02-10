import { useState, useCallback, useRef, useEffect } from 'react';

export interface CacheEntry<T> {
  data: T;
  timestamp: number;
  expiresAt: number;
}

export function useCache<T>(
  ttl: number = 5 * 60 * 1000
) {
  const cacheRef = useRef<Map<string, CacheEntry<T>>>(new Map());

  const get = useCallback(
    (key: string): T | null => {
      const entry = cacheRef.current.get(key);

      if (!entry) {
        return null;
      }

      if (Date.now() > entry.expiresAt) {
        cacheRef.current.delete(key);
        return null;
      }

      return entry.data;
    },
    []
  );

  const set = useCallback(
    (key: string, data: T, customTtl?: number) => {
      const now = Date.now();
      const expiresAt = now + (customTtl || ttl);

      cacheRef.current.set(key, {
        data,
        timestamp: now,
        expiresAt,
      });
    },
    [ttl]
  );

  const remove = useCallback((key: string) => {
    cacheRef.current.delete(key);
  }, []);

  const clear = useCallback(() => {
    cacheRef.current.clear();
  }, []);

  const has = useCallback(
    (key: string): boolean => {
      const entry = cacheRef.current.get(key);
      if (!entry) return false;

      if (Date.now() > entry.expiresAt) {
        cacheRef.current.delete(key);
        return false;
      }

      return true;
    },
    []
  );

  useEffect(() => {
    const interval = setInterval(() => {
      const now = Date.now();
      cacheRef.current.forEach((entry, key) => {
        if (now > entry.expiresAt) {
          cacheRef.current.delete(key);
        }
      });
    }, 60000);

    return () => clearInterval(interval);
  }, []);

  return {
    get,
    set,
    remove,
    clear,
    has,
  };
}


