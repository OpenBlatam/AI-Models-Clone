export type SortDirection = 'asc' | 'desc'

export interface SortConfig<T> {
  key: keyof T
  direction: SortDirection
}

export function sortBy<T>(
  items: T[],
  config: SortConfig<T>
): T[] {
  return [...items].sort((a, b) => {
    const aValue = a[config.key]
    const bValue = b[config.key]

    if (aValue === bValue) return 0

    const comparison = aValue < bValue ? -1 : 1
    return config.direction === 'asc' ? comparison : -comparison
  })
}

export function sortByMultiple<T>(
  items: T[],
  configs: SortConfig<T>[]
): T[] {
  return [...items].sort((a, b) => {
    for (const config of configs) {
      const aValue = a[config.key]
      const bValue = b[config.key]

      if (aValue !== bValue) {
        const comparison = aValue < bValue ? -1 : 1
        return config.direction === 'asc' ? comparison : -comparison
      }
    }
    return 0
  })
}


