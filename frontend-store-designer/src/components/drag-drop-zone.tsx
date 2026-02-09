'use client'

import { useState, useCallback, DragEvent } from 'react'
import { Upload, File } from 'lucide-react'
import { cn } from '@/lib/utils'

interface DragDropZoneProps {
  onDrop: (files: File[]) => void
  accept?: string
  maxFiles?: number
  className?: string
  children?: React.ReactNode
}

export function DragDropZone({
  onDrop,
  accept,
  maxFiles,
  className,
  children,
}: DragDropZoneProps) {
  const [isDragging, setIsDragging] = useState(false)

  const handleDragOver = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback(
    (e: DragEvent<HTMLDivElement>) => {
      e.preventDefault()
      e.stopPropagation()
      setIsDragging(false)

      const files = Array.from(e.dataTransfer.files)
      const filteredFiles = accept
        ? files.filter((file) => file.type.match(accept))
        : files

      const limitedFiles = maxFiles
        ? filteredFiles.slice(0, maxFiles)
        : filteredFiles

      if (limitedFiles.length > 0) {
        onDrop(limitedFiles)
      }
    },
    [onDrop, accept, maxFiles]
  )

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={cn(
        'border-2 border-dashed rounded-lg p-8 text-center transition-colors',
        isDragging
          ? 'border-blue-500 bg-blue-50'
          : 'border-gray-300 hover:border-gray-400',
        className
      )}
    >
      {children || (
        <>
          <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">
            Arrastra archivos aquí o haz clic para seleccionar
          </p>
        </>
      )}
    </div>
  )
}


