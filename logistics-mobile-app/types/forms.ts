// Form Types

export interface FormField<T = unknown> {
  value: T;
  error?: string;
  touched?: boolean;
  dirty?: boolean;
}

export interface FormState<T extends Record<string, unknown>> {
  fields: {
    [K in keyof T]: FormField<T[K]>;
  };
  isValid: boolean;
  isDirty: boolean;
  isSubmitting: boolean;
  submitCount: number;
}

export interface FormValidationRule<T = unknown> {
  required?: boolean;
  min?: number;
  max?: number;
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
  custom?: (value: T) => boolean | string;
  message?: string;
}

export interface FormValidationSchema<T extends Record<string, unknown>> {
  [K in keyof T]?: FormValidationRule<T[K]> | FormValidationRule<T[K]>[];
}

export interface FormSubmitHandler<T extends Record<string, unknown>> {
  (values: T): Promise<void> | void;
}

export interface FormChangeHandler<T extends Record<string, unknown>> {
  (field: keyof T, value: T[keyof T]): void;
}

export interface FormErrorHandler {
  (error: Error | unknown): void;
}

export interface UseFormReturn<T extends Record<string, unknown>> {
  values: T;
  errors: Partial<Record<keyof T, string>>;
  touched: Partial<Record<keyof T, boolean>>;
  isValid: boolean;
  isDirty: boolean;
  isSubmitting: boolean;
  setValue: (field: keyof T, value: T[keyof T]) => void;
  setError: (field: keyof T, error: string) => void;
  setTouched: (field: keyof T, touched: boolean) => void;
  handleChange: (field: keyof T) => (value: T[keyof T]) => void;
  handleBlur: (field: keyof T) => () => void;
  handleSubmit: (onSubmit: FormSubmitHandler<T>) => () => Promise<void>;
  reset: () => void;
  validate: () => boolean;
  validateField: (field: keyof T) => boolean;
}

