'use client'

import { useDesigns, useDeleteDesign } from '@/hooks/use-designs'
import { useDesignFilters } from '@/hooks/use-design-filters'
import { DesignCard } from './design-card'
import { DesignFilters } from './design-filters'
import { DesignCardSkeleton } from '@/components/design-card-skeleton'
import { EmptyState } from '@/components/empty-state'
import { ErrorMessage } from '@/components/error-message'
import { Store } from 'lucide-react'
import { useNavigation } from '@/utils/navigation'
import { useToast } from '@/components/ui/toast'

export function DesignList() {
  const { showToast } = useToast()
  const { goTo, refresh } = useNavigation()
  const { data, isLoading, error } = useDesigns()
  const deleteMutation = useDeleteDesign()
  const { filters, setFilters, filteredDesigns, clearFilters } = useDesignFilters(
    data?.items || []
  )

  const handleDelete = (storeId: string) => {
    if (confirm('¿Eliminar este diseño?')) {
      deleteMutation.mutate(storeId, {
        onSuccess: () => showToast('Diseño eliminado', 'success'),
        onError: (error: Error) =>
          showToast(error.message || 'Error al eliminar', 'error'),
      })
    }
  }

  if (isLoading) {
    return (
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[1, 2, 3].map((i) => (
          <DesignCardSkeleton key={i} />
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <ErrorMessage
        message="Error al cargar diseños"
        onRetry={() => refresh()}
      />
    )
  }

  return (
    <>
      <DesignFilters filters={filters} onFiltersChange={setFilters} />

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredDesigns.map((design) => (
          <DesignCard
            key={design.store_id}
            design={design}
            onDelete={handleDelete}
            isDeleting={deleteMutation.isPending}
          />
        ))}
      </div>

      {filteredDesigns.length === 0 && data?.items && data.items.length > 0 && (
        <div className="col-span-full">
          <EmptyState
            title="No se encontraron diseños"
            description="No hay diseños que coincidan con los filtros aplicados"
            action={{
              label: 'Limpiar Filtros',
              onClick: clearFilters,
            }}
          />
        </div>
      )}

      {data?.items.length === 0 && (
        <EmptyState
          title="No tienes diseños aún"
          description="Comienza creando tu primer diseño de local"
          icon={<Store className="w-12 h-12 text-gray-400" />}
          action={{
            label: 'Crear Primer Diseño',
            onClick: () => goTo('/design'),
          }}
        />
      )}
    </>
  )
}

