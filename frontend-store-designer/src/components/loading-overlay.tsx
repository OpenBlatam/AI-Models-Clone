import { LoadingSpinner } from './loading-spinner'

interface LoadingOverlayProps {
  message?: string
}

export function LoadingOverlay({ message = 'Cargando...' }: LoadingOverlayProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-white rounded-lg p-6 shadow-xl flex flex-col items-center gap-4">
        <LoadingSpinner size="lg" />
        <p className="text-gray-600">{message}</p>
      </div>
    </div>
  )
}


