import { useEffect, useRef, useState } from 'react'

interface UseInfiniteScrollOptions {
  threshold?: number
  rootMargin?: string
  enabled?: boolean
}

export function useInfiniteScroll(
  callback: () => void,
  options: UseInfiniteScrollOptions = {}
) {
  const { threshold = 0.1, rootMargin = '100px', enabled = true } = options
  const [isFetching, setIsFetching] = useState(false)
  const observerRef = useRef<IntersectionObserver | null>(null)
  const elementRef = useRef<HTMLElement | null>(null)

  useEffect(() => {
    if (!enabled || !elementRef.current) return

    observerRef.current = new IntersectionObserver(
      (entries) => {
        const [entry] = entries
        if (entry.isIntersecting && !isFetching) {
          setIsFetching(true)
          callback()
        }
      },
      { threshold, rootMargin }
    )

    observerRef.current.observe(elementRef.current)

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect()
      }
    }
  }, [callback, threshold, rootMargin, enabled, isFetching])

  const resetFetching = () => setIsFetching(false)

  return { elementRef, isFetching, resetFetching }
}


