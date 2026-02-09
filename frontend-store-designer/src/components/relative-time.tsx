'use client'

import { formatRelativeTime, formatDistanceTime } from '@/utils/date'

interface RelativeTimeProps {
  date: Date | string
  variant?: 'relative' | 'distance'
  className?: string
}

export function RelativeTime({
  date,
  variant = 'relative',
  className,
}: RelativeTimeProps) {
  const formatted =
    variant === 'relative' ? formatRelativeTime(date) : formatDistanceTime(date)

  return (
    <time dateTime={typeof date === 'string' ? date : date.toISOString()} className={className}>
      {formatted}
    </time>
  )
}


