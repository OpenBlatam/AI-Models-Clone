import { Badge } from '@/components/ui/badge'
import { CheckCircle2, Clock, XCircle, AlertCircle } from 'lucide-react'
import { cn } from '@/lib/utils'

type Status = 'success' | 'pending' | 'error' | 'warning'

interface StatusBadgeProps {
  status: Status
  label?: string
  className?: string
}

const statusConfig: Record<
  Status,
  { label: string; icon: typeof CheckCircle2; variant: 'default' | 'destructive' | 'secondary' | 'outline' }
> = {
  success: {
    label: 'Completado',
    icon: CheckCircle2,
    variant: 'default',
  },
  pending: {
    label: 'Pendiente',
    icon: Clock,
    variant: 'secondary',
  },
  error: {
    label: 'Error',
    icon: XCircle,
    variant: 'destructive',
  },
  warning: {
    label: 'Advertencia',
    icon: AlertCircle,
    variant: 'outline',
  },
}

export function StatusBadge({ status, label, className }: StatusBadgeProps) {
  const config = statusConfig[status]
  const Icon = config.icon

  return (
    <Badge variant={config.variant} className={cn('gap-1', className)}>
      <Icon className="w-3 h-3" />
      {label || config.label}
    </Badge>
  )
}


