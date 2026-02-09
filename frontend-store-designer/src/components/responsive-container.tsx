'use client'

import { useWindowSize } from '@/hooks/use-window-size'
import { ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface ResponsiveContainerProps {
  children: ReactNode
  breakpoints?: {
    sm?: string
    md?: string
    lg?: string
    xl?: string
  }
  className?: string
}

export function ResponsiveContainer({
  children,
  breakpoints,
  className,
}: ResponsiveContainerProps) {
  const { width } = useWindowSize()

  const getSize = () => {
    if (width >= 1280) return breakpoints?.xl || 'xl'
    if (width >= 1024) return breakpoints?.lg || 'lg'
    if (width >= 768) return breakpoints?.md || 'md'
    return breakpoints?.sm || 'sm'
  }

  return (
    <div className={cn('responsive-container', `size-${getSize()}`, className)}>
      {children}
    </div>
  )
}


