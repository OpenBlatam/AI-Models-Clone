import { format as dateFnsFormat, formatDistance, isToday, isTomorrow, isYesterday } from 'date-fns';

export function formatEventTime(date: Date | string): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  
  if (isToday(dateObj)) {
    return `Today, ${dateFnsFormat(dateObj, 'h:mm a')}`;
  }
  
  if (isTomorrow(dateObj)) {
    return `Tomorrow, ${dateFnsFormat(dateObj, 'h:mm a')}`;
  }
  
  if (isYesterday(dateObj)) {
    return `Yesterday, ${dateFnsFormat(dateObj, 'h:mm a')}`;
  }
  
  return dateFnsFormat(dateObj, 'MMM d, h:mm a');
}

export function formatEventDate(date: Date | string): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  return dateFnsFormat(dateObj, 'MMMM d, yyyy');
}

export function formatRelativeTime(date: Date | string): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  return formatDistance(dateObj, new Date(), { addSuffix: true });
}

export function formatDuration(minutes: number): string {
  if (minutes < 60) {
    return `${minutes}m`;
  }
  
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  
  if (remainingMinutes === 0) {
    return `${hours}h`;
  }
  
  return `${hours}h ${remainingMinutes}m`;
}

export function formatPriority(priority: number): string {
  if (priority >= 8) return 'High';
  if (priority >= 5) return 'Medium';
  return 'Low';
}


