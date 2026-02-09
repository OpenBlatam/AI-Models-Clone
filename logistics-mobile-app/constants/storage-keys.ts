// AsyncStorage Keys
export const STORAGE_KEYS = {
  // Authentication
  AUTH_TOKEN: 'auth_token',
  REFRESH_TOKEN: 'refresh_token',
  USER_DATA: 'user_data',
  SESSION_ID: 'session_id',

  // Settings
  THEME_MODE: 'theme_mode',
  LANGUAGE: 'language',
  NOTIFICATIONS_ENABLED: 'notifications_enabled',
  BIOMETRIC_ENABLED: 'biometric_enabled',

  // App State
  ONBOARDING_COMPLETED: 'onboarding_completed',
  LAST_SYNC: 'last_sync',
  CACHE_VERSION: 'cache_version',

  // User Preferences
  PREFERRED_TRANSPORT_MODE: 'preferred_transport_mode',
  DEFAULT_CURRENCY: 'default_currency',
  DATE_FORMAT: 'date_format',
  TIME_FORMAT: 'time_format',

  // Offline Data
  OFFLINE_SHIPMENTS: 'offline_shipments',
  OFFLINE_QUOTES: 'offline_quotes',
  PENDING_UPLOADS: 'pending_uploads',

  // Search & Filters
  RECENT_SEARCHES: 'recent_searches',
  SAVED_FILTERS: 'saved_filters',

  // Analytics
  ANALYTICS_ID: 'analytics_id',
  INSTALL_DATE: 'install_date',
} as const;

// Secure Storage Keys (for sensitive data)
export const SECURE_STORAGE_KEYS = {
  AUTH_TOKEN: 'secure_auth_token',
  REFRESH_TOKEN: 'secure_refresh_token',
  BIOMETRIC_KEY: 'biometric_key',
  ENCRYPTION_KEY: 'encryption_key',
} as const;


