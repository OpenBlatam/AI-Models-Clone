// Animation Durations
export const ANIMATION_DURATION = {
  FAST: 150,
  NORMAL: 300,
  SLOW: 500,
  VERY_SLOW: 800,
} as const;

// Debounce & Throttle Delays
export const DELAYS = {
  DEBOUNCE_SEARCH: 500,
  DEBOUNCE_INPUT: 300,
  THROTTLE_SCROLL: 100,
  THROTTLE_RESIZE: 200,
} as const;

// Polling Intervals
export const POLLING_INTERVALS = {
  TRACKING: 30000, // 30 seconds
  DASHBOARD: 60000, // 1 minute
  ALERTS: 60000, // 1 minute
  NETWORK_CHECK: 5000, // 5 seconds
} as const;

// Time Constants
export const TIME = {
  SECOND: 1000,
  MINUTE: 60 * 1000,
  HOUR: 60 * 60 * 1000,
  DAY: 24 * 60 * 60 * 1000,
  WEEK: 7 * 24 * 60 * 60 * 1000,
  MONTH: 30 * 24 * 60 * 60 * 1000,
} as const;

// Cache TTL
export const CACHE_TTL = {
  SHORT: 1 * TIME.MINUTE,
  MEDIUM: 5 * TIME.MINUTE,
  LONG: 15 * TIME.MINUTE,
  VERY_LONG: 60 * TIME.MINUTE,
} as const;

// Retry Delays
export const RETRY_DELAYS = {
  IMMEDIATE: 0,
  SHORT: 1 * TIME.SECOND,
  MEDIUM: 3 * TIME.SECOND,
  LONG: 5 * TIME.SECOND,
} as const;


