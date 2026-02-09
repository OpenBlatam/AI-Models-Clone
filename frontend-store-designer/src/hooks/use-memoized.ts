import { useMemo } from 'react'

export function useMemoized<T>(
  factory: () => T,
  deps: React.DependencyList
): T {
  return useMemo(factory, deps)
}


