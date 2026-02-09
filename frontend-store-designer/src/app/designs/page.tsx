'use client'

import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { DesignList } from '@/components/designs/design-list'
import { useDesigns } from '@/hooks/use-designs'
import { PageHeader } from '@/components/layout/page-header'

export default function DesignsPage() {
  const { data } = useDesigns()

  return (
    <div className="container mx-auto px-4 py-8">
      <PageHeader
        title="Mis Diseños"
        description={`${data?.items.length || 0} diseño${(data?.items.length || 0) !== 1 ? 's' : ''}`}
        action={
          <Link href="/design">
            <Button>Crear Nuevo Diseño</Button>
          </Link>
        }
      />
      <DesignList />
    </div>
  )
}

