'use client'

import { X } from 'lucide-react'
import { Badge } from './ui/badge'
import { cn } from '@/lib/utils'

interface FilterChip {
  label: string
  value: string
}

interface FilterChipsProps {
  filters: FilterChip[]
  onRemove: (value: string) => void
  onClearAll?: () => void
  className?: string
}

export function FilterChips({
  filters,
  onRemove,
  onClearAll,
  className,
}: FilterChipsProps) {
  if (filters.length === 0) return null

  return (
    <div className={cn('flex flex-wrap gap-2 items-center', className)}>
      {filters.map((filter) => (
        <Badge
          key={filter.value}
          variant="secondary"
          className="gap-1 pr-1"
        >
          {filter.label}
          <button
            onClick={() => onRemove(filter.value)}
            className="ml-1 hover:bg-gray-300 rounded-full p-0.5"
            aria-label={`Remove ${filter.label}`}
          >
            <X className="w-3 h-3" />
          </button>
        </Badge>
      ))}
      {onClearAll && (
        <button
          onClick={onClearAll}
          className="text-sm text-blue-600 hover:text-blue-700"
        >
          Limpiar todo
        </button>
      )}
    </div>
  )
}


