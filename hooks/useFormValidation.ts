import { useState, useCallback, useEffect } from 'react';
import { z, ZodSchema, ZodError } from 'zod';

export interface ValidationRule {
  type: 'required' | 'minLength' | 'maxLength' | 'pattern' | 'custom' | 'email' | 'url' | 'number';
  value?: any;
  message: string;
}

export interface FieldValidation {
  value: any;
  error: string | null;
  isValid: boolean;
  isTouched: boolean;
  isDirty: boolean;
}

export interface FormValidationState<T> {
  values: T;
  errors: Partial<Record<keyof T, string>>;
  touched: Partial<Record<keyof T, boolean>>;
  dirty: Partial<Record<keyof T, boolean>>;
  isValid: boolean;
  isSubmitting: boolean;
  submitCount: number;
}

export interface UseFormValidationOptions<T> {
  initialValues: T;
  validationSchema?: ZodSchema<T>;
  validationRules?: Partial<Record<keyof T, ValidationRule[]>>;
  onSubmit?: (values: T) => Promise<void> | void;
  onError?: (errors: Partial<Record<keyof T, string>>) => void;
  validateOnChange?: boolean;
  validateOnBlur?: boolean;
  validateOnSubmit?: boolean;
}

/**
 * Advanced form validation hook with Zod schema support
 */
export function useFormValidation<T extends Record<string, any>>({
  initialValues,
  validationSchema,
  validationRules,
  onSubmit,
  onError,
  validateOnChange = true,
  validateOnBlur = true,
  validateOnSubmit = true,
}: UseFormValidationOptions<T>) {
  const [state, setState] = useState<FormValidationState<T>>({
    values: initialValues,
    errors: {},
    touched: {},
    dirty: {},
    isValid: true,
    isSubmitting: false,
    submitCount: 0,
  });

  // Validate a single field
  const validateField = useCallback(
    (field: keyof T, value: any): string | null => {
      // Zod schema validation
      if (validationSchema) {
        try {
          const fieldSchema = z.object({ [field]: validationSchema.shape[field] });
          fieldSchema.parse({ [field]: value });
        } catch (error) {
          if (error instanceof ZodError) {
            const fieldError = error.errors.find(e => e.path.includes(field as string));
            if (fieldError) {
              return fieldError.message;
            }
          }
        }
      }

      // Custom validation rules
      if (validationRules && validationRules[field]) {
        const rules = validationRules[field]!;
        
        for (const rule of rules) {
          switch (rule.type) {
            case 'required':
              if (!value || (typeof value === 'string' && value.trim() === '')) {
                return rule.message || 'This field is required';
              }
              break;
              
            case 'minLength':
              if (typeof value === 'string' && value.length < rule.value) {
                return rule.message || `Minimum length is ${rule.value} characters`;
              }
              break;
              
            case 'maxLength':
              if (typeof value === 'string' && value.length > rule.value) {
                return rule.message || `Maximum length is ${rule.value} characters`;
              }
              break;
              
            case 'pattern':
              if (rule.value && typeof value === 'string' && !rule.value.test(value)) {
                return rule.message || 'Invalid format';
              }
              break;
              
            case 'email':
              const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
              if (value && !emailRegex.test(value)) {
                return rule.message || 'Invalid email format';
              }
              break;
              
            case 'url':
              try {
                if (value && new URL(value)) {
                  // URL is valid
                }
              } catch {
                return rule.message || 'Invalid URL format';
              }
              break;
              
            case 'number':
              if (value && isNaN(Number(value))) {
                return rule.message || 'Must be a valid number';
              }
              break;
              
            case 'custom':
              if (rule.value && typeof rule.value === 'function') {
                try {
                  const result = rule.value(value);
                  if (result !== true) {
                    return result || rule.message || 'Invalid value';
                  }
                } catch (error) {
                  return rule.message || 'Validation failed';
                }
              }
              break;
          }
        }
      }

      return null;
    },
    [validationSchema, validationRules]
  );

  // Validate all fields
  const validateForm = useCallback((): Partial<Record<keyof T, string>> => {
    const errors: Partial<Record<keyof T, string>> = {};
    
    Object.keys(state.values).forEach(field => {
      const fieldKey = field as keyof T;
      const error = validateField(fieldKey, state.values[fieldKey]);
      if (error) {
        errors[fieldKey] = error;
      }
    });

    return errors;
  }, [state.values, validateField]);

  // Update field value
  const setFieldValue = useCallback(
    (field: keyof T, value: any) => {
      setState(prev => {
        const newValues = { ...prev.values, [field]: value };
        const newDirty = { ...prev.dirty, [field]: value !== initialValues[field] };
        
        let newErrors = { ...prev.errors };
        let newTouched = { ...prev.touched };
        
        // Validate on change if enabled
        if (validateOnChange) {
          const error = validateField(field, value);
          if (error) {
            newErrors[field] = error;
          } else {
            delete newErrors[field];
          }
        }
        
        // Mark as touched
        newTouched[field] = true;
        
        // Check overall validity
        const isValid = Object.keys(newErrors).length === 0;
        
        return {
          ...prev,
          values: newValues,
          errors: newErrors,
          touched: newTouched,
          dirty: newDirty,
          isValid,
        };
      });
    },
    [validateOnChange, validateField, initialValues]
  );

  // Handle field blur
  const handleFieldBlur = useCallback(
    (field: keyof T) => {
      if (validateOnBlur) {
        const error = validateField(field, state.values[field]);
        setState(prev => ({
          ...prev,
          errors: {
            ...prev.errors,
            [field]: error || undefined,
          },
          touched: {
            ...prev.touched,
            [field]: true,
          },
        }));
      }
    },
    [validateOnBlur, validateField, state.values]
  );

  // Reset form
  const resetForm = useCallback(() => {
    setState({
      values: initialValues,
      errors: {},
      touched: {},
      dirty: {},
      isValid: true,
      isSubmitting: false,
      submitCount: 0,
    });
  }, [initialValues]);

  // Set form values
  const setValues = useCallback((values: Partial<T>) => {
    setState(prev => {
      const newValues = { ...prev.values, ...values };
      const newDirty = { ...prev.dirty };
      
      // Update dirty state for changed fields
      Object.keys(values).forEach(field => {
        const fieldKey = field as keyof T;
        newDirty[fieldKey] = values[fieldKey] !== initialValues[fieldKey];
      });
      
      return {
        ...prev,
        values: newValues,
        dirty: newDirty,
      };
    });
  }, [initialValues]);

  // Set field error
  const setFieldError = useCallback((field: keyof T, error: string | null) => {
    setState(prev => ({
      ...prev,
      errors: {
        ...prev.errors,
        [field]: error || undefined,
      },
    }));
  }, []);

  // Set multiple field errors
  const setErrors = useCallback((errors: Partial<Record<keyof T, string>>) => {
    setState(prev => ({
      ...prev,
      errors: { ...prev.errors, ...errors },
    }));
  }, []);

  // Handle form submission
  const handleSubmit = useCallback(
    async (event?: React.FormEvent) => {
      if (event) {
        event.preventDefault();
      }

      setState(prev => ({ ...prev, isSubmitting: true }));

      try {
        // Validate form before submission
        if (validateOnSubmit) {
          const errors = validateForm();
          if (Object.keys(errors).length > 0) {
            setState(prev => ({
              ...prev,
              errors,
              isValid: false,
              isSubmitting: false,
            }));
            
            if (onError) {
              onError(errors);
            }
            return;
          }
        }

        // Call onSubmit if provided
        if (onSubmit) {
          await onSubmit(state.values);
        }

        // Increment submit count on success
        setState(prev => ({
          ...prev,
          submitCount: prev.submitCount + 1,
          isSubmitting: false,
        }));
      } catch (error) {
        setState(prev => ({ ...prev, isSubmitting: false }));
        throw error;
      }
    },
    [validateOnSubmit, validateForm, onSubmit, onError, state.values]
  );

  // Get field validation state
  const getFieldState = useCallback(
    (field: keyof T): FieldValidation => ({
      value: state.values[field],
      error: state.errors[field] || null,
      isValid: !state.errors[field],
      isTouched: !!state.touched[field],
      isDirty: !!state.dirty[field],
    }),
    [state]
  );

  // Check if form is valid
  useEffect(() => {
    const errors = validateForm();
    const isValid = Object.keys(errors).length === 0;
    
    setState(prev => ({
      ...prev,
      errors,
      isValid,
    }));
  }, [state.values, validateForm]);

  return {
    // State
    values: state.values,
    errors: state.errors,
    touched: state.touched,
    dirty: state.dirty,
    isValid: state.isValid,
    isSubmitting: state.isSubmitting,
    submitCount: state.submitCount,
    
    // Actions
    setFieldValue,
    setValues,
    setFieldError,
    setErrors,
    handleFieldBlur,
    handleSubmit,
    resetForm,
    validateField,
    validateForm,
    
    // Utilities
    getFieldState,
    
    // Form helpers
    register: (field: keyof T) => ({
      value: state.values[field],
      onChange: (value: any) => setFieldValue(field, value),
      onBlur: () => handleFieldBlur(field),
      error: state.errors[field],
      isTouched: !!state.touched[field],
      isDirty: !!state.dirty[field],
    }),
  };
}
