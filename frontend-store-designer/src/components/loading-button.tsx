'use client'

import { Button, ButtonProps } from './ui/button'
import { LoadingSpinner } from './loading-spinner'
import { cn } from '@/lib/utils'

interface LoadingButtonProps extends ButtonProps {
  isLoading?: boolean
  loadingText?: string
}

export function LoadingButton({
  isLoading,
  loadingText,
  children,
  disabled,
  className,
  ...props
}: LoadingButtonProps) {
  return (
    <Button
      disabled={disabled || isLoading}
      className={cn(className)}
      {...props}
    >
      {isLoading && <LoadingSpinner size="sm" className="mr-2" />}
      {isLoading && loadingText ? loadingText : children}
    </Button>
  )
}


