'use client'

import { Select } from './ui/select'
import { ArrowUpDown } from 'lucide-react'

export type SortOption = {
  value: string
  label: string
}

interface SortSelectProps {
  options: SortOption[]
  value: string
  onChange: (value: string) => void
  className?: string
}

export function SortSelect({
  options,
  value,
  onChange,
  className,
}: SortSelectProps) {
  return (
    <div className={`flex items-center gap-2 ${className || ''}`}>
      <ArrowUpDown className="w-4 h-4 text-gray-400" />
      <Select value={value} onValueChange={onChange}>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </Select>
    </div>
  )
}


