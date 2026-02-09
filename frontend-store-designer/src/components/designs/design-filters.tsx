'use client'

import { SearchFilter } from '@/components/search-filter'
import { StoreType, DesignStyle } from '@/types'
import type { FilterOptions } from '@/utils/filters'

interface DesignFiltersProps {
  filters: FilterOptions
  onFiltersChange: (filters: FilterOptions) => void
}

export function DesignFilters({ filters, onFiltersChange }: DesignFiltersProps) {
  return (
    <SearchFilter
      onSearch={(query) => onFiltersChange({ ...filters, searchQuery: query })}
      onFilterType={(type) =>
        onFiltersChange({ ...filters, type: type as StoreType | 'all' })
      }
      onFilterStyle={(style) =>
        onFiltersChange({ ...filters, style: style as DesignStyle | 'all' })
      }
    />
  )
}


