'use client'

import Image from 'next/image'
import { useState } from 'react'
import { cn } from '@/lib/utils'
import { ImageIcon } from 'lucide-react'

interface ImageOptimizedProps {
  src?: string
  alt: string
  width?: number
  height?: number
  className?: string
  fallback?: React.ReactNode
}

export function ImageOptimized({
  src,
  alt,
  width = 800,
  height = 600,
  className,
  fallback,
}: ImageOptimizedProps) {
  const [error, setError] = useState(false)

  if (!src || error) {
    return (
      <div
        className={cn(
          'bg-gray-100 flex items-center justify-center',
          className
        )}
        style={{ width, height }}
      >
        {fallback || <ImageIcon className="w-12 h-12 text-gray-400" />}
      </div>
    )
  }

  return (
    <Image
      src={src}
      alt={alt}
      width={width}
      height={height}
      className={className}
      onError={() => setError(true)}
      loading="lazy"
    />
  )
}


