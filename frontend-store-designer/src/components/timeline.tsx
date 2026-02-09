'use client'

import { CheckCircle2, Circle } from 'lucide-react'
import { cn } from '@/lib/utils'

interface TimelineItem {
  title: string
  description?: string
  completed: boolean
  date?: string
}

interface TimelineProps {
  items: TimelineItem[]
}

export function Timeline({ items }: TimelineProps) {
  return (
    <div className="space-y-4">
      {items.map((item, idx) => (
        <div key={idx} className="flex gap-4">
          <div className="flex flex-col items-center">
            {item.completed ? (
              <CheckCircle2 className="w-6 h-6 text-green-600" />
            ) : (
              <Circle className="w-6 h-6 text-gray-300" />
            )}
            {idx < items.length - 1 && (
              <div
                className={cn(
                  'w-0.5 flex-1 mt-2',
                  item.completed ? 'bg-green-600' : 'bg-gray-300'
                )}
              />
            )}
          </div>
          <div className="flex-1 pb-4">
            <div className="flex items-center justify-between">
              <h4
                className={cn(
                  'font-medium',
                  item.completed ? 'text-gray-900' : 'text-gray-500'
                )}
              >
                {item.title}
              </h4>
              {item.date && (
                <span className="text-xs text-gray-500">{item.date}</span>
              )}
            </div>
            {item.description && (
              <p className="text-sm text-gray-600 mt-1">{item.description}</p>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}


