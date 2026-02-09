import Link from 'next/link'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { formatDate } from '@/lib/utils'
import { getStoreTypeLabel, getDesignStyleLabel } from '@/constants/store-types'
import type { StoreDesign } from '@/types'

interface DesignCardProps {
  design: StoreDesign
  onDelete?: (storeId: string) => void
  isDeleting?: boolean
}

export function DesignCard({ design, onDelete, isDeleting }: DesignCardProps) {
  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader>
        <CardTitle>{design.store_name}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div className="flex gap-2 flex-wrap">
            <Badge variant="secondary">{getStoreTypeLabel(design.store_type)}</Badge>
            <Badge variant="outline">{getDesignStyleLabel(design.style)}</Badge>
          </div>
          <p className="text-xs text-gray-500">
            Creado: {formatDate(design.created_at)}
          </p>
          <div className="flex gap-2 mt-4">
            <Link href={`/designs/${design.store_id}`} className="flex-1">
              <Button className="w-full">Ver Detalles</Button>
            </Link>
            {onDelete && (
              <Button
                variant="destructive"
                size="sm"
                onClick={() => onDelete(design.store_id)}
                disabled={isDeleting}
              >
                🗑️
              </Button>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

