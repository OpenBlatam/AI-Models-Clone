// Validation Rules
export const VALIDATION = {
  // Email
  EMAIL_REGEX: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,

  // Phone
  PHONE_REGEX: /^\+?[1-9]\d{1,14}$/,

  // Password
  PASSWORD_MIN_LENGTH: 8,
  PASSWORD_REGEX: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/,

  // Text Lengths
  MIN_LENGTH: {
    NAME: 2,
    DESCRIPTION: 10,
    ADDRESS: 5,
    CITY: 2,
    COUNTRY: 2,
  },
  MAX_LENGTH: {
    NAME: 100,
    DESCRIPTION: 1000,
    ADDRESS: 200,
    CITY: 100,
    COUNTRY: 100,
    NOTES: 500,
  },

  // Numbers
  MIN_VALUE: {
    WEIGHT: 0.1, // kg
    VOLUME: 0.01, // m³
    QUANTITY: 1,
    PRICE: 0.01,
  },
  MAX_VALUE: {
    WEIGHT: 100000, // kg
    VOLUME: 10000, // m³
    QUANTITY: 1000000,
    PRICE: 1000000000,
  },

  // Coordinates
  LATITUDE: {
    MIN: -90,
    MAX: 90,
  },
  LONGITUDE: {
    MIN: -180,
    MAX: 180,
  },

  // File Sizes (in bytes)
  FILE_SIZE: {
    MAX_IMAGE: 10 * 1024 * 1024, // 10MB
    MAX_DOCUMENT: 50 * 1024 * 1024, // 50MB
    MAX_VIDEO: 100 * 1024 * 1024, // 100MB
  },

  // File Types
  ALLOWED_IMAGE_TYPES: ['image/jpeg', 'image/png', 'image/webp', 'image/jpg'],
  ALLOWED_DOCUMENT_TYPES: [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  ],
} as const;

// Error Messages
export const VALIDATION_MESSAGES = {
  REQUIRED: 'This field is required',
  EMAIL: 'Please enter a valid email address',
  PHONE: 'Please enter a valid phone number',
  PASSWORD: 'Password must be at least 8 characters with uppercase, lowercase, number and special character',
  MIN_LENGTH: (min: number) => `Must be at least ${min} characters`,
  MAX_LENGTH: (max: number) => `Must be no more than ${max} characters`,
  MIN_VALUE: (min: number) => `Must be at least ${min}`,
  MAX_VALUE: (max: number) => `Must be no more than ${max}`,
  INVALID_FORMAT: 'Invalid format',
  FILE_TOO_LARGE: (maxSize: string) => `File size must be less than ${maxSize}`,
  INVALID_FILE_TYPE: 'Invalid file type',
} as const;


