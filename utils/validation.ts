import { useState, useCallback } from 'react';

type ValidationRule<T> = (value: T) => string | null;
type ValidationResult = { isValid: boolean; errors: string[] };

// Core validation functions
export const isRequired = <T>(value: T): string | null => {
  return value === null || value === undefined || value === '' ? 'This field is required' : null;
};

export const isEmail = (value: string): string | null => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(value) ? null : 'Invalid email format';
};

export const isMinLength = (minLength: number) => (value: string): string | null => {
  return value.length >= minLength ? null : `Minimum length is ${minLength} characters`;
};

export const isMaxLength = (maxLength: number) => (value: string): string | null => {
  return value.length <= maxLength ? null : `Maximum length is ${maxLength} characters`;
};

export const isPattern = (pattern: RegExp, message: string) => (value: string): string | null => {
  return pattern.test(value) ? null : message;
};

export const isNumber = (value: string): string | null => {
  return !isNaN(Number(value)) ? null : 'Must be a valid number';
};

export const isPositive = (value: number): string | null => {
  return value > 0 ? null : 'Must be a positive number';
};

export const isInRange = (min: number, max: number) => (value: number): string | null => {
  return value >= min && value <= max ? null : `Must be between ${min} and ${max}`;
};

// Composite validation
export const validateField = <T>(value: T, rules: ValidationRule<T>[]): ValidationResult => {
  const errors = rules
    .map(rule => rule(value))
    .filter(error => error !== null) as string[];

  return {
    isValid: errors.length === 0,
    errors,
  };
};

export const validateForm = <T extends Record<string, any>>(
  values: T,
  rules: Record<keyof T, ValidationRule<T[keyof T]>[]>
): Record<keyof T, ValidationResult> => {
  const results = {} as Record<keyof T, ValidationResult>;

  Object.keys(rules).forEach(key => {
    const fieldKey = key as keyof T;
    results[fieldKey] = validateField(values[fieldKey], rules[fieldKey]);
  });

  return results;
};

// Predefined validation schemas
export const validationSchemas = {
  email: [isRequired, isEmail],
  password: [isRequired, isMinLength(6), isMaxLength(128)],
  username: [isRequired, isMinLength(3), isMaxLength(20), isPattern(/^[a-zA-Z0-9_]+$/, 'Only letters, numbers, and underscores allowed')],
  phone: [isPattern(/^\+?[\d\s\-\(\)]+$/, 'Invalid phone number format')],
  url: [isPattern(/^https?:\/\/.+/, 'Must be a valid URL starting with http:// or https://')],
  age: [isNumber, isPositive, isInRange(0, 120)],
};

// Form validation hook
export const useFormValidation = <T extends Record<string, any>>(
  initialValues: T,
  validationRules: Record<keyof T, ValidationRule<T[keyof T]>[]>
) => {
  const [values, setValues] = useState<T>(initialValues);
  const [errors, setErrors] = useState<Record<keyof T, string[]>>({} as Record<keyof T, string[]>);
  const [touched, setTouched] = useState<Record<keyof T, boolean>>({} as Record<keyof T, boolean>);

  const validateField = useCallback((field: keyof T, value: T[keyof T]) => {
    const fieldRules = validationRules[field];
    const result = validateField(value, fieldRules);
    setErrors(prev => ({ ...prev, [field]: result.errors }));
    return result.isValid;
  }, [validationRules]);

  const setValue = useCallback((field: keyof T, value: T[keyof T]) => {
    setValues(prev => ({ ...prev, [field]: value }));
    if (touched[field]) {
      validateField(field, value);
    }
  }, [touched, validateField]);

  const setTouchedField = useCallback((field: keyof T, isTouched: boolean = true) => {
    setTouched(prev => ({ ...prev, [field]: isTouched }));
    if (isTouched) {
      validateField(field, values[field]);
    }
  }, [values, validateField]);

  const validateAll = useCallback(() => {
    const results = validateForm(values, validationRules);
    setErrors(Object.keys(results).reduce((acc, key) => {
      acc[key as keyof T] = results[key as keyof T].errors;
      return acc;
    }, {} as Record<keyof T, string[]>));
    return Object.values(results).every(result => result.isValid);
  }, [values, validationRules]);

  const reset = useCallback(() => {
    setValues(initialValues);
    setErrors({} as Record<keyof T, string[]>);
    setTouched({} as Record<keyof T, boolean>);
  }, [initialValues]);

  return {
    values,
    errors,
    touched,
    setValue,
    setTouchedField,
    validateAll,
    reset,
    isValid: Object.keys(errors).every(key => errors[key as keyof T].length === 0),
  };
}; 