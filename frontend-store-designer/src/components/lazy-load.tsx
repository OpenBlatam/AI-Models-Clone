'use client'

import { Suspense, ReactNode } from 'react'
import { LoadingSpinner } from './loading-spinner'

interface LazyLoadProps {
  children: ReactNode
  fallback?: ReactNode
}

export function LazyLoad({ children, fallback }: LazyLoadProps) {
  return (
    <Suspense fallback={fallback || <LoadingSpinner />}>
      {children}
    </Suspense>
  )
}


