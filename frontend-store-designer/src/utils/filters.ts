import type { StoreDesign, StoreType, DesignStyle } from '@/types'

export interface FilterOptions {
  searchQuery: string
  type: StoreType | 'all'
  style: DesignStyle | 'all'
}

export function filterDesigns(
  designs: StoreDesign[],
  filters: FilterOptions
): StoreDesign[] {
  return designs.filter((design) => {
    const matchesSearch =
      filters.searchQuery === '' ||
      design.store_name.toLowerCase().includes(filters.searchQuery.toLowerCase()) ||
      design.description.toLowerCase().includes(filters.searchQuery.toLowerCase())

    const matchesType =
      filters.type === 'all' || design.store_type === filters.type

    const matchesStyle =
      filters.style === 'all' || design.style === filters.style

    return matchesSearch && matchesType && matchesStyle
  })
}


