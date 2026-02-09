import { useState, useCallback } from 'react'
import { cache } from '@/utils/cache'

export function useCache<T>(key: string, ttl = 5 * 60 * 1000) {
  const [data, setData] = useState<T | null>(() => cache.get<T>(key))

  const setCached = useCallback(
    (value: T) => {
      cache.set(key, value, ttl)
      setData(value)
    },
    [key, ttl]
  )

  const clearCache = useCallback(() => {
    cache.delete(key)
    setData(null)
  }, [key])

  return { data, setCached, clearCache }
}


