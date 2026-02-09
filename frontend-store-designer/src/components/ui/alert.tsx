import * as React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'
import { AlertCircle, CheckCircle2, Info, AlertTriangle, X } from 'lucide-react'

const alertVariants = cva(
  'relative w-full rounded-lg border p-4',
  {
    variants: {
      variant: {
        default: 'bg-background text-foreground',
        destructive: 'border-red-500/50 text-red-900 dark:text-red-50',
        success: 'border-green-500/50 text-green-900 dark:text-green-50',
        warning: 'border-yellow-500/50 text-yellow-900 dark:text-yellow-50',
        info: 'border-blue-500/50 text-blue-900 dark:text-blue-50',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
)

const iconMap = {
  destructive: AlertCircle,
  success: CheckCircle2,
  warning: AlertTriangle,
  info: Info,
  default: Info,
}

export interface AlertProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof alertVariants> {
  title?: string
  onClose?: () => void
}

const Alert = React.forwardRef<HTMLDivElement, AlertProps>(
  ({ className, variant, title, onClose, children, ...props }, ref) => {
    const Icon = variant ? iconMap[variant] : iconMap.default

    return (
      <div
        ref={ref}
        role="alert"
        className={cn(alertVariants({ variant }), className)}
        {...props}
      >
        <div className="flex items-start gap-3">
          {variant && variant !== 'default' && (
            <Icon className="h-5 w-5 mt-0.5 flex-shrink-0" />
          )}
          <div className="flex-1">
            {title && <h4 className="font-semibold mb-1">{title}</h4>}
            <div className="text-sm">{children}</div>
          </div>
          {onClose && (
            <button
              onClick={onClose}
              className="absolute right-2 top-2 text-gray-400 hover:text-gray-600"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>
      </div>
    )
  }
)
Alert.displayName = 'Alert'

export { Alert, alertVariants }


