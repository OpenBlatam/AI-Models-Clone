import { format, formatDistance, formatRelative, parseISO, isValid } from 'date-fns';

// Date Formatting
export function formatDate(date: Date | string | null | undefined, formatStr: string = 'MMM dd, yyyy'): string {
  if (!date) return '';
  
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    if (!isValid(dateObj)) return '';
    return format(dateObj, formatStr);
  } catch {
    return '';
  }
}

export function formatDateTime(date: Date | string | null | undefined): string {
  return formatDate(date, 'MMM dd, yyyy HH:mm');
}

export function formatTime(date: Date | string | null | undefined): string {
  return formatDate(date, 'HH:mm');
}

export function formatRelativeTime(date: Date | string | null | undefined): string {
  if (!date) return '';
  
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    if (!isValid(dateObj)) return '';
    return formatRelative(dateObj, new Date());
  } catch {
    return '';
  }
}

export function formatDistanceTime(date: Date | string | null | undefined): string {
  if (!date) return '';
  
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    if (!isValid(dateObj)) return '';
    return formatDistance(dateObj, new Date(), { addSuffix: true });
  } catch {
    return '';
  }
}

// Number Formatting
export function formatNumber(value: number | null | undefined, decimals: number = 2): string {
  if (value === null || value === undefined || isNaN(value)) return '0';
  return value.toFixed(decimals);
}

export function formatCurrency(
  value: number | null | undefined,
  currency: string = 'USD',
  locale: string = 'en-US'
): string {
  if (value === null || value === undefined || isNaN(value)) return `0.00 ${currency}`;
  
  try {
    return new Intl.NumberFormat(locale, {
      style: 'currency',
      currency,
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value);
  } catch {
    return `${value.toFixed(2)} ${currency}`;
  }
}

export function formatPercentage(value: number | null | undefined, decimals: number = 1): string {
  if (value === null || value === undefined || isNaN(value)) return '0%';
  return `${value.toFixed(decimals)}%`;
}

export function formatLargeNumber(value: number | null | undefined): string {
  if (value === null || value === undefined || isNaN(value)) return '0';
  
  if (value >= 1000000) {
    return `${(value / 1000000).toFixed(1)}M`;
  }
  if (value >= 1000) {
    return `${(value / 1000).toFixed(1)}K`;
  }
  return value.toString();
}

// Weight & Volume Formatting
export function formatWeight(kg: number | null | undefined, unit: 'kg' | 'lb' = 'kg'): string {
  if (kg === null || kg === undefined || isNaN(kg)) return `0 ${unit}`;
  
  if (unit === 'lb') {
    const pounds = kg * 2.20462;
    return `${formatNumber(pounds, 2)} lb`;
  }
  return `${formatNumber(kg, 2)} kg`;
}

export function formatVolume(m3: number | null | undefined, unit: 'm3' | 'ft3' = 'm3'): string {
  if (m3 === null || m3 === undefined || isNaN(m3)) return `0 ${unit}`;
  
  if (unit === 'ft3') {
    const cubicFeet = m3 * 35.3147;
    return `${formatNumber(cubicFeet, 2)} ft³`;
  }
  return `${formatNumber(m3, 2)} m³`;
}

// Duration Formatting
export function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds}s`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h`;
  return `${Math.floor(seconds / 86400)}d`;
}

export function formatTransitDays(days: number): string {
  if (days === 0) return 'Same day';
  if (days === 1) return '1 day';
  return `${days} days`;
}

// Phone Number Formatting
export function formatPhoneNumber(phone: string | null | undefined): string {
  if (!phone) return '';
  
  const cleaned = phone.replace(/\D/g, '');
  
  if (cleaned.length === 10) {
    return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6)}`;
  }
  if (cleaned.length === 11 && cleaned[0] === '1') {
    return `+1 (${cleaned.slice(1, 4)}) ${cleaned.slice(4, 7)}-${cleaned.slice(7)}`;
  }
  
  return phone;
}

// File Size Formatting
export function formatFileSize(bytes: number | null | undefined): string {
  if (bytes === null || bytes === undefined || bytes === 0) return '0 B';
  
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return `${formatNumber(bytes / Math.pow(k, i), 1)} ${sizes[i]}`;
}

// Status Formatting
export function formatStatus(status: string): string {
  return status
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
}

// Tracking Number Formatting
export function formatTrackingNumber(trackingNumber: string | null | undefined): string {
  if (!trackingNumber) return '';
  
  // Format as groups of 4 characters
  return trackingNumber.replace(/(.{4})/g, '$1 ').trim();
}


