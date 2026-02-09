import { Search } from 'lucide-react'
import { EmptyState } from './empty-state'

interface EmptySearchProps {
  query: string
  onClear: () => void
}

export function EmptySearch({ query, onClear }: EmptySearchProps) {
  return (
    <EmptyState
      title="No se encontraron resultados"
      description={`No hay resultados para "${query}"`}
      icon={<Search className="w-12 h-12 text-gray-400" />}
      action={{
        label: 'Limpiar búsqueda',
        onClick: onClear,
      }}
    />
  )
}


