'use client'

import { ReactNode, useMemo } from 'react'

interface VirtualListProps<T> {
  items: T[]
  renderItem: (item: T, index: number) => ReactNode
  itemHeight?: number
  containerHeight?: number
  overscan?: number
}

export function VirtualList<T>({
  items,
  renderItem,
  itemHeight = 100,
  containerHeight = 600,
  overscan = 3,
}: VirtualListProps<T>) {
  const visibleItems = useMemo(() => {
    const visibleCount = Math.ceil(containerHeight / itemHeight)
    return items.slice(0, visibleCount + overscan)
  }, [items, itemHeight, containerHeight, overscan])

  return (
    <div style={{ height: containerHeight, overflow: 'auto' }}>
      {visibleItems.map((item, index) => (
        <div key={index} style={{ height: itemHeight }}>
          {renderItem(item, index)}
        </div>
      ))}
    </div>
  )
}


