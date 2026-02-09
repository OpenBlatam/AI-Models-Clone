'use client'

import { HelpCircle } from 'lucide-react'
import { Tooltip } from './tooltip'

interface HelpTooltipProps {
  content: string
  className?: string
}

export function HelpTooltip({ content, className }: HelpTooltipProps) {
  return (
    <Tooltip content={content} position="right">
      <HelpCircle className={className || 'w-4 h-4 text-gray-400'} />
    </Tooltip>
  )
}


