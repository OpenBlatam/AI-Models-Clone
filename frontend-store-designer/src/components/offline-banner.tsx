'use client'

import { useOnlineStatus } from '@/hooks/use-online-status'
import { Alert } from './ui/alert'
import { WifiOff } from 'lucide-react'

export function OfflineBanner() {
  const isOnline = useOnlineStatus()

  if (isOnline) return null

  return (
    <Alert variant="warning" className="m-4">
      <WifiOff className="w-4 h-4" />
      <span>Estás sin conexión. Algunas funciones pueden no estar disponibles.</span>
    </Alert>
  )
}


