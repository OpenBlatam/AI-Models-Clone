'use client'

import { useState } from 'react'
import { Edit2, Check, X } from 'lucide-react'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { cn } from '@/lib/utils'

interface InlineEditProps {
  value: string
  onSave: (value: string) => void
  className?: string
  placeholder?: string
}

export function InlineEdit({
  value,
  onSave,
  className,
  placeholder,
}: InlineEditProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [editValue, setEditValue] = useState(value)

  const handleSave = () => {
    onSave(editValue)
    setIsEditing(false)
  }

  const handleCancel = () => {
    setEditValue(value)
    setIsEditing(false)
  }

  if (isEditing) {
    return (
      <div className="flex items-center gap-2">
        <Input
          value={editValue}
          onChange={(e) => setEditValue(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') handleSave()
            if (e.key === 'Escape') handleCancel()
          }}
          placeholder={placeholder}
          autoFocus
          className={className}
        />
        <Button size="sm" onClick={handleSave}>
          <Check className="w-4 h-4" />
        </Button>
        <Button size="sm" variant="outline" onClick={handleCancel}>
          <X className="w-4 h-4" />
        </Button>
      </div>
    )
  }

  return (
    <div className="flex items-center gap-2 group">
      <span className={cn(className)}>{value}</span>
      <Button
        variant="ghost"
        size="sm"
        onClick={() => setIsEditing(true)}
        className="opacity-0 group-hover:opacity-100 transition-opacity"
      >
        <Edit2 className="w-4 h-4" />
      </Button>
    </div>
  )
}


