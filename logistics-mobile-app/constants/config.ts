import Constants from 'expo-constants';

// App Configuration
export const APP_CONFIG = {
  NAME: 'Logistics AI Platform',
  VERSION: Constants.expoConfig?.version || '1.0.0',
  BUILD_NUMBER: Constants.expoConfig?.ios?.buildNumber || Constants.expoConfig?.android?.versionCode || '1',
  BUNDLE_ID: Constants.expoConfig?.ios?.bundleIdentifier || Constants.expoConfig?.android?.package || '',
  SCHEME: Constants.expoConfig?.scheme || 'logistics',
} as const;

// Environment
export const ENV = {
  DEVELOPMENT: __DEV__,
  PRODUCTION: !__DEV__,
  TEST: process.env.NODE_ENV === 'test',
} as const;

// Feature Flags
export const FEATURES = {
  OFFLINE_MODE: true,
  BIOMETRIC_AUTH: true,
  PUSH_NOTIFICATIONS: true,
  ANALYTICS: true,
  CRASH_REPORTING: true,
  DEEP_LINKING: true,
  SHARE_FUNCTIONALITY: true,
} as const;

// Limits
export const LIMITS = {
  MAX_UPLOAD_SIZE: 50 * 1024 * 1024, // 50MB
  MAX_ITEMS_PER_PAGE: 50,
  MAX_SEARCH_RESULTS: 100,
  MAX_RECENT_SEARCHES: 10,
  MAX_SAVED_FILTERS: 5,
  MAX_RETRY_ATTEMPTS: 3,
} as const;

// Timeouts
export const TIMEOUTS = {
  API_REQUEST: 30000, // 30 seconds
  IMAGE_LOAD: 10000, // 10 seconds
  CONNECTION_CHECK: 5000, // 5 seconds
  SPLASH_SCREEN: 3000, // 3 seconds
} as const;

// Pagination
export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 20,
  MAX_PAGE_SIZE: 100,
  DEFAULT_PAGE: 1,
} as const;

// Refresh Intervals
export const REFRESH_INTERVALS = {
  TRACKING: 30000, // 30 seconds
  DASHBOARD: 60000, // 1 minute
  ALERTS: 60000, // 1 minute
  SYNC: 5 * 60 * 1000, // 5 minutes
} as const;


