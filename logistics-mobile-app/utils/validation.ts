import { VALIDATION, VALIDATION_MESSAGES } from '@/constants';

// Email Validation
export function isValidEmail(email: string | null | undefined): boolean {
  if (!email) return false;
  return VALIDATION.EMAIL_REGEX.test(email.trim());
}

// Phone Validation
export function isValidPhone(phone: string | null | undefined): boolean {
  if (!phone) return false;
  return VALIDATION.PHONE_REGEX.test(phone.trim());
}

// Password Validation
export function isValidPassword(password: string | null | undefined): boolean {
  if (!password) return false;
  if (password.length < VALIDATION.PASSWORD_MIN_LENGTH) return false;
  return VALIDATION.PASSWORD_REGEX.test(password);
}

// Required Field Validation
export function isRequired(value: unknown): boolean {
  if (value === null || value === undefined) return false;
  if (typeof value === 'string') return value.trim().length > 0;
  if (Array.isArray(value)) return value.length > 0;
  return true;
}

// Length Validation
export function isValidLength(
  value: string | null | undefined,
  min: number,
  max: number
): boolean {
  if (!value) return false;
  const length = value.trim().length;
  return length >= min && length <= max;
}

// Number Range Validation
export function isInRange(value: number | null | undefined, min: number, max: number): boolean {
  if (value === null || value === undefined || isNaN(value)) return false;
  return value >= min && value <= max;
}

// Coordinate Validation
export function isValidLatitude(lat: number | null | undefined): boolean {
  if (lat === null || lat === undefined || isNaN(lat)) return false;
  return lat >= VALIDATION.LATITUDE.MIN && lat <= VALIDATION.LATITUDE.MAX;
}

export function isValidLongitude(lng: number | null | undefined): boolean {
  if (lng === null || lng === undefined || isNaN(lng)) return false;
  return lng >= VALIDATION.LONGITUDE.MIN && lng <= VALIDATION.LONGITUDE.MAX;
}

// File Size Validation
export function isValidFileSize(size: number, maxSize: number = VALIDATION.FILE_SIZE.MAX_DOCUMENT): boolean {
  return size <= maxSize;
}

// File Type Validation
export function isValidImageType(mimeType: string): boolean {
  return VALIDATION.ALLOWED_IMAGE_TYPES.includes(mimeType);
}

export function isValidDocumentType(mimeType: string): boolean {
  return VALIDATION.ALLOWED_DOCUMENT_TYPES.includes(mimeType);
}

// URL Validation
export function isValidUrl(url: string | null | undefined): boolean {
  if (!url) return false;
  
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

// Date Validation
export function isValidDate(date: Date | string | null | undefined): boolean {
  if (!date) return false;
  
  try {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    return !isNaN(dateObj.getTime());
  } catch {
    return false;
  }
}

// Future Date Validation
export function isFutureDate(date: Date | string | null | undefined): boolean {
  if (!isValidDate(date)) return false;
  
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  return dateObj > new Date();
}

// Past Date Validation
export function isPastDate(date: Date | string | null | undefined): boolean {
  if (!isValidDate(date)) return false;
  
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  return dateObj < new Date();
}

// Get Validation Error Message
export function getValidationMessage(field: string, errorType: string, value?: unknown): string {
  const messages: Record<string, string> = {
    required: VALIDATION_MESSAGES.REQUIRED,
    email: VALIDATION_MESSAGES.EMAIL,
    phone: VALIDATION_MESSAGES.PHONE,
    password: VALIDATION_MESSAGES.PASSWORD,
    invalidFormat: VALIDATION_MESSAGES.INVALID_FORMAT,
  };

  if (errorType === 'minLength' && typeof value === 'number') {
    return VALIDATION_MESSAGES.MIN_LENGTH(value);
  }
  if (errorType === 'maxLength' && typeof value === 'number') {
    return VALIDATION_MESSAGES.MAX_LENGTH(value);
  }
  if (errorType === 'minValue' && typeof value === 'number') {
    return VALIDATION_MESSAGES.MIN_VALUE(value);
  }
  if (errorType === 'maxValue' && typeof value === 'number') {
    return VALIDATION_MESSAGES.MAX_VALUE(value);
  }

  return messages[errorType] || VALIDATION_MESSAGES.INVALID_FORMAT;
}


