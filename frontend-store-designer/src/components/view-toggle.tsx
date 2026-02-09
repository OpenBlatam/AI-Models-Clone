'use client'

import { LayoutGrid, List } from 'lucide-react'
import { Button } from './ui/button'
import { cn } from '@/lib/utils'

type ViewMode = 'grid' | 'list'

interface ViewToggleProps {
  value: ViewMode
  onChange: (mode: ViewMode) => void
  className?: string
}

export function ViewToggle({ value, onChange, className }: ViewToggleProps) {
  return (
    <div className={cn('flex gap-1 border rounded-lg p-1', className)}>
      <Button
        variant={value === 'grid' ? 'default' : 'ghost'}
        size="sm"
        onClick={() => onChange('grid')}
        className="gap-2"
      >
        <LayoutGrid className="w-4 h-4" />
        <span className="hidden sm:inline">Grid</span>
      </Button>
      <Button
        variant={value === 'list' ? 'default' : 'ghost'}
        size="sm"
        onClick={() => onChange('list')}
        className="gap-2"
      >
        <List className="w-4 h-4" />
        <span className="hidden sm:inline">Lista</span>
      </Button>
    </div>
  )
}


