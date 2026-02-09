import { useState, useMemo } from 'react'
import { filterDesigns, type FilterOptions } from '@/utils/filters'
import type { StoreDesign } from '@/types'

export function useDesignFilters(designs: StoreDesign[] = []) {
  const [filters, setFilters] = useState<FilterOptions>({
    searchQuery: '',
    type: 'all',
    style: 'all',
  })

  const filteredDesigns = useMemo(() => {
    return filterDesigns(designs, filters)
  }, [designs, filters])

  const clearFilters = () => {
    setFilters({ searchQuery: '', type: 'all', style: 'all' })
  }

  return {
    filters,
    setFilters,
    filteredDesigns,
    clearFilters,
  }
}


