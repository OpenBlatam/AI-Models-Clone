type DateFormat = 'short' | 'medium' | 'long' | 'full' | 'relative';
type TimeUnit = 'second' | 'minute' | 'hour' | 'day' | 'week' | 'month' | 'year';

interface DateOptions {
  format?: DateFormat;
  locale?: string;
  timeZone?: string;
}

interface RelativeTimeOptions {
  unit?: TimeUnit;
  threshold?: number;
}

// Core date formatting
export const formatDate = (date: Date, options: DateOptions = {}): string => {
  const { format = 'medium', locale = 'en-US', timeZone = 'UTC' } = options;
  
  const formatOptions: Intl.DateTimeFormatOptions = {
    timeZone,
    ...(format === 'short' && { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    }),
    ...(format === 'medium' && { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }),
    ...(format === 'long' && { 
      weekday: 'long',
      year: 'numeric', 
      month: 'long', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    }),
    ...(format === 'full' && { 
      weekday: 'long',
      year: 'numeric', 
      month: 'long', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      timeZoneName: 'long'
    }),
  };

  return new Intl.DateTimeFormat(locale, formatOptions).format(date);
};

// Relative time formatting
export const formatRelativeTime = (date: Date, options: RelativeTimeOptions = {}): string => {
  const { unit = 'minute', threshold = 1 } = options;
  const now = new Date();
  const diffInMs = now.getTime() - date.getTime();
  
  const units: Record<TimeUnit, number> = {
    second: 1000,
    minute: 60 * 1000,
    hour: 60 * 60 * 1000,
    day: 24 * 60 * 60 * 1000,
    week: 7 * 24 * 60 * 60 * 1000,
    month: 30 * 24 * 60 * 60 * 1000,
    year: 365 * 24 * 60 * 60 * 1000,
  };

  const diffInUnits = Math.floor(diffInMs / units[unit]);
  
  if (diffInUnits < threshold) {
    return 'just now';
  }

  const rtf = new Intl.RelativeTimeFormat('en', { numeric: 'auto' });
  return rtf.format(-diffInUnits, unit);
};

// Date manipulation utilities
export const dateUtils = {
  addDays: (date: Date, days: number): Date => {
    const result = new Date(date);
    result.setDate(result.getDate() + days);
    return result;
  },

  addMonths: (date: Date, months: number): Date => {
    const result = new Date(date);
    result.setMonth(result.getMonth() + months);
    return result;
  },

  addYears: (date: Date, years: number): Date => {
    const result = new Date(date);
    result.setFullYear(result.getFullYear() + years);
    return result;
  },

  startOfDay: (date: Date): Date => {
    const result = new Date(date);
    result.setHours(0, 0, 0, 0);
    return result;
  },

  endOfDay: (date: Date): Date => {
    const result = new Date(date);
    result.setHours(23, 59, 59, 999);
    return result;
  },

  startOfWeek: (date: Date, firstDayOfWeek: number = 0): Date => {
    const result = new Date(date);
    const day = result.getDay();
    const diff = result.getDate() - day + (day === 0 ? -6 : firstDayOfWeek);
    result.setDate(diff);
    return dateUtils.startOfDay(result);
  },

  endOfWeek: (date: Date, firstDayOfWeek: number = 0): Date => {
    const start = dateUtils.startOfWeek(date, firstDayOfWeek);
    return dateUtils.addDays(start, 6);
  },

  isToday: (date: Date): boolean => {
    const today = new Date();
    return dateUtils.startOfDay(date).getTime() === dateUtils.startOfDay(today).getTime();
  },

  isYesterday: (date: Date): boolean => {
    const yesterday = dateUtils.addDays(new Date(), -1);
    return dateUtils.startOfDay(date).getTime() === dateUtils.startOfDay(yesterday).getTime();
  },

  isThisWeek: (date: Date): boolean => {
    const thisWeekStart = dateUtils.startOfWeek(new Date());
    const thisWeekEnd = dateUtils.endOfWeek(new Date());
    return date >= thisWeekStart && date <= thisWeekEnd;
  },

  isThisMonth: (date: Date): boolean => {
    const now = new Date();
    return date.getMonth() === now.getMonth() && date.getFullYear() === now.getFullYear();
  },

  isThisYear: (date: Date): boolean => {
    return date.getFullYear() === new Date().getFullYear();
  },

  getDaysInMonth: (date: Date): number => {
    return new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();
  },

  getWeekNumber: (date: Date): number => {
    const startOfYear = new Date(date.getFullYear(), 0, 1);
    const days = Math.floor((date.getTime() - startOfYear.getTime()) / (24 * 60 * 60 * 1000));
    return Math.ceil((days + startOfYear.getDay() + 1) / 7);
  },

  getAge: (birthDate: Date): number => {
    const today = new Date();
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    
    return age;
  },
};

// Date parsing utilities
export const parseDate = (dateString: string, format?: string): Date => {
  if (format === 'ISO') {
    return new Date(dateString);
  }
  
  // Handle common date formats
  const patterns = [
    /^\d{4}-\d{2}-\d{2}$/, // YYYY-MM-DD
    /^\d{2}\/\d{2}\/\d{4}$/, // MM/DD/YYYY
    /^\d{2}-\d{2}-\d{4}$/, // MM-DD-YYYY
  ];

  for (const pattern of patterns) {
    if (pattern.test(dateString)) {
      return new Date(dateString);
    }
  }

  throw new Error(`Unable to parse date: ${dateString}`);
};

// Date validation
export const isValidDate = (date: any): boolean => {
  return date instanceof Date && !isNaN(date.getTime());
};

// Date comparison utilities
export const dateComparison = {
  isBefore: (date1: Date, date2: Date): boolean => date1 < date2,
  isAfter: (date1: Date, date2: Date): boolean => date1 > date2,
  isSame: (date1: Date, date2: Date): boolean => date1.getTime() === date2.getTime(),
  isSameDay: (date1: Date, date2: Date): boolean => {
    return dateUtils.startOfDay(date1).getTime() === dateUtils.startOfDay(date2).getTime();
  },
  isSameMonth: (date1: Date, date2: Date): boolean => {
    return date1.getMonth() === date2.getMonth() && date1.getFullYear() === date2.getFullYear();
  },
  isSameYear: (date1: Date, date2: Date): boolean => {
    return date1.getFullYear() === date2.getFullYear();
  },
}; 