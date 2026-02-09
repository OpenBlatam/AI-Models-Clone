import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { ReactNode } from 'react'

interface EmptyStateProps {
  title: string
  description: string
  action?: {
    label: string
    onClick: () => void
  }
  icon?: ReactNode
}

export function EmptyState({ title, description, action, icon }: EmptyStateProps) {
  return (
    <Card>
      <CardContent className="py-12 text-center">
        {icon && <div className="mb-4 flex justify-center">{icon}</div>}
        <h3 className="text-lg font-semibold mb-2">{title}</h3>
        <p className="text-gray-600 mb-4">{description}</p>
        {action && <Button onClick={action.onClick}>{action.label}</Button>}
      </CardContent>
    </Card>
  )
}


