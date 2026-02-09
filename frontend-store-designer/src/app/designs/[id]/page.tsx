'use client'

import { useParams } from 'next/navigation'
import { useDesign, useDesigns } from '@/hooks/use-designs'
import { useAnalysis } from '@/hooks/use-analysis'
import { useExport } from '@/hooks/use-export'
import { useDeleteConfirmation } from '@/hooks/use-delete-confirmation'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { LoadingSpinner } from '@/components/loading-spinner'
import { EmptyState } from '@/components/empty-state'
import { BackButton } from '@/components/actions'
import { DesignHeader } from '@/components/design-detail/design-header'
import { DesignOverview } from '@/components/design-detail/design-overview'
import { DesignAnalysis } from '@/components/design-detail/design-analysis'
import { MarketingPlanView, DecorationPlanView, PriceBreakdown } from '@/components/plans'
import { useRouter } from 'next/navigation'

export default function DesignDetailPage() {
  const params = useParams()
  const router = useRouter()
  const storeId = params.id as string

  const { data: design, isLoading } = useDesign(storeId)
  const { data: analysis } = useAnalysis(storeId)
  const { data: designsData } = useDesigns(1, 100)
  const { exportDesign, isExporting } = useExport(storeId)
  const {
    showModal: showDeleteModal,
    setShowModal: setShowDeleteModal,
    handleDelete,
    isDeleting,
  } = useDeleteConfirmation(storeId)

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <LoadingSpinner size="lg" text="Cargando diseño..." />
      </div>
    )
  }

  if (!design) {
    return (
      <div className="container mx-auto px-4 py-8">
        <EmptyState
          title="Diseño no encontrado"
          description="El diseño que buscas no existe o fue eliminado"
          action={{
            label: 'Volver a Diseños',
            onClick: () => router.push('/designs'),
          }}
        />
      </div>
    )
  }


  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      <BackButton href="/designs" />
      <DesignHeader
        design={design}
        storeId={storeId}
        onExport={exportDesign}
        onDelete={handleDelete}
        isExporting={isExporting}
        isDeleting={isDeleting}
        showDeleteModal={showDeleteModal}
        setShowDeleteModal={setShowDeleteModal}
      />

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Resumen</TabsTrigger>
          <TabsTrigger value="marketing">Marketing</TabsTrigger>
          <TabsTrigger value="decoration">Decoración</TabsTrigger>
          <TabsTrigger value="analysis">Análisis</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <DesignOverview design={design} />
        </TabsContent>

        <TabsContent value="marketing" className="space-y-4">
          <MarketingPlanView plan={design.marketing_plan} />
        </TabsContent>

        <TabsContent value="decoration" className="space-y-4">
          <DecorationPlanView plan={design.decoration_plan} />
          <PriceBreakdown plan={design.decoration_plan} />
        </TabsContent>

        <TabsContent value="analysis" className="space-y-4">
          <DesignAnalysis
            design={design}
            storeId={storeId}
            analysis={analysis}
            designsData={designsData}
          />
        </TabsContent>
      </Tabs>
    </div>
  )
}

