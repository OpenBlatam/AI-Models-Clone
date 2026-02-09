'use client'

import { useEffect } from 'react'
import { Button } from '@/components/ui/button'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error(error)
  }, [error])

  return (
    <div className="container mx-auto px-4 py-16 text-center">
      <h1 className="text-4xl font-bold mb-4">Algo salió mal</h1>
      <p className="text-gray-600 mb-8">{error.message}</p>
      <Button onClick={reset}>Intentar de nuevo</Button>
    </div>
  )
}


