// Date utilities with TypeScript

export const formatDate = (date: Date, options: Intl.DateTimeFormatOptions = {}): string => {
  const defaultOptions: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    ...options,
  };
  
  return new Intl.DateTimeFormat('en-US', defaultOptions).format(date);
};

export const formatRelativeTime = (date: Date): string => {
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);
  
  const intervals = {
    year: 31536000,
    month: 2592000,
    week: 604800,
    day: 86400,
    hour: 3600,
    minute: 60,
  };
  
  for (const [unit, seconds] of Object.entries(intervals)) {
    const interval = Math.floor(diffInSeconds / seconds);
    if (interval >= 1) {
      return `${interval} ${unit}${interval === 1 ? '' : 's'} ago`;
    }
  }
  
  return 'Just now';
};

export const addDays = (date: Date, days: number): Date => {
  const result = new Date(date);
  result.setDate(result.getDate() + days);
  return result;
};

export const addMonths = (date: Date, months: number): Date => {
  const result = new Date(date);
  result.setMonth(result.getMonth() + months);
  return result;
};

export const addYears = (date: Date, years: number): Date => {
  const result = new Date(date);
  result.setFullYear(result.getFullYear() + years);
  return result;
};

export const startOfDay = (date: Date): Date => {
  const result = new Date(date);
  result.setHours(0, 0, 0, 0);
  return result;
};

export const endOfDay = (date: Date): Date => {
  const result = new Date(date);
  result.setHours(23, 59, 59, 999);
  return result;
};

export const startOfWeek = (date: Date, firstDayOfWeek: number = 0): Date => {
  const result = new Date(date);
  const day = result.getDay();
  const diff = result.getDate() - day + (day === 0 ? -6 : firstDayOfWeek);
  result.setDate(diff);
  return startOfDay(result);
};

export const endOfWeek = (date: Date, firstDayOfWeek: number = 0): Date => {
  const result = startOfWeek(date, firstDayOfWeek);
  result.setDate(result.getDate() + 6);
  return endOfDay(result);
};

export const isSameDay = (date1: Date, date2: Date): boolean => {
  return (
    date1.getFullYear() === date2.getFullYear() &&
    date1.getMonth() === date2.getMonth() &&
    date1.getDate() === date2.getDate()
  );
};

export const isToday = (date: Date): boolean => {
  return isSameDay(date, new Date());
};

export const isYesterday = (date: Date): boolean => {
  return isSameDay(date, addDays(new Date(), -1));
};

export const isTomorrow = (date: Date): boolean => {
  return isSameDay(date, addDays(new Date(), 1));
};

export const getDaysInMonth = (year: number, month: number): number => {
  return new Date(year, month + 1, 0).getDate();
};

export const getWeekNumber = (date: Date): number => {
  const firstDayOfYear = new Date(date.getFullYear(), 0, 1);
  const pastDaysOfYear = (date.getTime() - firstDayOfYear.getTime()) / 86400000;
  return Math.ceil((pastDaysOfYear + firstDayOfYear.getDay() + 1) / 7);
};

// Date range utilities
export const getDateRange = (start: Date, end: Date): Date[] => {
  const dates: Date[] = [];
  const current = new Date(start);
  
  while (current <= end) {
    dates.push(new Date(current));
    current.setDate(current.getDate() + 1);
  }
  
  return dates;
};

export const isDateInRange = (date: Date, start: Date, end: Date): boolean => {
  return date >= start && date <= end;
};

// Timezone utilities
export const formatInTimezone = (
  date: Date,
  timezone: string,
  options: Intl.DateTimeFormatOptions = {}
): string => {
  return new Intl.DateTimeFormat('en-US', {
    timeZone: timezone,
    ...options,
  }).format(date);
};

export const convertTimezone = (date: Date, fromTz: string, toTz: string): Date => {
  const fromDate = new Date(date.toLocaleString('en-US', { timeZone: fromTz }));
  const toDate = new Date(date.toLocaleString('en-US', { timeZone: toTz }));
  const diff = fromDate.getTime() - toDate.getTime();
  
  return new Date(date.getTime() + diff);
}; 