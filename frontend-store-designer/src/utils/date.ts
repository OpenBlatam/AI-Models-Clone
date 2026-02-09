import { format, formatDistance, formatRelative, isToday, isYesterday } from 'date-fns'
import { es } from 'date-fns/locale'

export function formatDate(date: Date | string): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date
  return format(dateObj, 'PPP', { locale: es })
}

export function formatDateTime(date: Date | string): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date
  return format(dateObj, 'PPP p', { locale: es })
}

export function formatRelativeTime(date: Date | string): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date
  
  if (isToday(dateObj)) {
    return 'Hoy'
  }
  
  if (isYesterday(dateObj)) {
    return 'Ayer'
  }
  
  return formatRelative(dateObj, new Date(), { locale: es })
}

export function formatDistanceTime(date: Date | string): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date
  return formatDistance(dateObj, new Date(), { addSuffix: true, locale: es })
}


