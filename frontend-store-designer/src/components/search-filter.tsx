'use client'

import { useState } from 'react'
import { Input } from '@/components/ui/input'
import { Select } from '@/components/ui/select'
import { Search, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { StoreType, DesignStyle } from '@/types'
import { getStoreTypeLabel, getDesignStyleLabel } from '@/constants/store-types'

interface SearchFilterProps {
  onSearch: (query: string) => void
  onFilterType: (type: StoreType | 'all') => void
  onFilterStyle: (style: DesignStyle | 'all') => void
}

export function SearchFilter({
  onSearch,
  onFilterType,
  onFilterStyle,
}: SearchFilterProps) {
  const [searchQuery, setSearchQuery] = useState('')

  const handleSearch = (value: string) => {
    setSearchQuery(value)
    onSearch(value)
  }

  const clearSearch = () => {
    setSearchQuery('')
    onSearch('')
  }

  return (
    <div className="flex flex-col md:flex-row gap-4 mb-6">
      <div className="flex-1 relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
        <Input
          type="text"
          placeholder="Buscar diseños..."
          value={searchQuery}
          onChange={(e) => handleSearch(e.target.value)}
          className="pl-10 pr-10"
        />
        {searchQuery && (
          <button
            onClick={clearSearch}
            className="absolute right-3 top-1/2 transform -translate-y-1/2"
          >
            <X className="w-4 h-4 text-gray-400" />
          </button>
        )}
      </div>
      <Select
        onChange={(e) => onFilterType(e.target.value as StoreType | 'all')}
        defaultValue="all"
      >
        <option value="all">Todos los tipos</option>
        {Object.values(StoreType).map((type) => (
          <option key={type} value={type}>
            {getStoreTypeLabel(type)}
          </option>
        ))}
      </Select>
      <Select
        onChange={(e) => onFilterStyle(e.target.value as DesignStyle | 'all')}
        defaultValue="all"
      >
        <option value="all">Todos los estilos</option>
        {Object.values(DesignStyle).map((style) => (
          <option key={style} value={style}>
            {getDesignStyleLabel(style)}
          </option>
        ))}
      </Select>
    </div>
  )
}

