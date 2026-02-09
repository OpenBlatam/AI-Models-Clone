// Success Messages
export const SUCCESS_MESSAGES = {
  QUOTE_CREATED: 'Quote created successfully',
  BOOKING_CREATED: 'Booking created successfully',
  SHIPMENT_CREATED: 'Shipment created successfully',
  DOCUMENT_UPLOADED: 'Document uploaded successfully',
  INVOICE_CREATED: 'Invoice created successfully',
  ALERT_CREATED: 'Alert created successfully',
  SETTINGS_SAVED: 'Settings saved successfully',
  PROFILE_UPDATED: 'Profile updated successfully',
  PASSWORD_CHANGED: 'Password changed successfully',
  DATA_SYNCED: 'Data synced successfully',
} as const;

// Error Messages
export const ERROR_MESSAGES = {
  // Network
  NETWORK_ERROR: 'Network error. Please check your connection.',
  TIMEOUT_ERROR: 'Request timed out. Please try again.',
  OFFLINE: 'You are currently offline. Please check your connection.',

  // API
  SERVER_ERROR: 'Server error. Please try again later.',
  NOT_FOUND: 'Resource not found.',
  UNAUTHORIZED: 'You are not authorized to perform this action.',
  FORBIDDEN: 'Access denied.',
  VALIDATION_ERROR: 'Please check your input and try again.',

  // Actions
  CREATE_FAILED: 'Failed to create. Please try again.',
  UPDATE_FAILED: 'Failed to update. Please try again.',
  DELETE_FAILED: 'Failed to delete. Please try again.',
  UPLOAD_FAILED: 'Failed to upload. Please try again.',
  DOWNLOAD_FAILED: 'Failed to download. Please try again.',

  // Permissions
  CAMERA_PERMISSION: 'Camera permission is required to take photos.',
  LOCATION_PERMISSION: 'Location permission is required for tracking.',
  STORAGE_PERMISSION: 'Storage permission is required to save files.',

  // General
  UNKNOWN_ERROR: 'An unexpected error occurred. Please try again.',
  RETRY_LATER: 'Please try again later.',
} as const;

// Info Messages
export const INFO_MESSAGES = {
  LOADING: 'Loading...',
  SAVING: 'Saving...',
  UPLOADING: 'Uploading...',
  DOWNLOADING: 'Downloading...',
  SYNCING: 'Syncing...',
  NO_DATA: 'No data available',
  NO_RESULTS: 'No results found',
  PULL_TO_REFRESH: 'Pull to refresh',
  SWIPE_TO_DELETE: 'Swipe to delete',
} as const;

// Warning Messages
export const WARNING_MESSAGES = {
  UNSAVED_CHANGES: 'You have unsaved changes. Are you sure you want to leave?',
  DELETE_CONFIRMATION: 'Are you sure you want to delete this item?',
  OFFLINE_MODE: 'You are in offline mode. Some features may be limited.',
  OLD_DATA: 'Data may be outdated. Please refresh.',
} as const;

// Placeholder Messages
export const PLACEHOLDERS = {
  SEARCH: 'Search...',
  EMAIL: 'email@example.com',
  PHONE: '+1 (555) 123-4567',
  NAME: 'Enter name',
  ADDRESS: 'Enter address',
  CITY: 'Enter city',
  COUNTRY: 'Enter country',
  DESCRIPTION: 'Enter description',
  NOTES: 'Enter notes (optional)',
  QUANTITY: '0',
  WEIGHT: '0.00',
  PRICE: '0.00',
} as const;


