'use client';

import { useState, useCallback } from 'react';
import { z } from 'zod';

export interface ValidationError {
  field: string;
  message: string;
}

export interface FormValidationState<T> {
  values: T;
  errors: ValidationError[];
  isValid: boolean;
  isSubmitting: boolean;
  touched: Set<string>;
}

export function useFormValidation<T extends Record<string, any>>(
  schema: z.ZodSchema<T>,
  initialValues: T
) {
  const [state, setState] = useState<FormValidationState<T>>({
    values: initialValues,
    errors: [],
    isValid: true,
    isSubmitting: false,
    touched: new Set(),
  });

  // Validate a single field
  const validateField = useCallback(
    (field: keyof T, value: any): string | null => {
      try {
        // Create a partial schema for the specific field
        const fieldSchema = schema.pick({ [field]: true } as any);
        fieldSchema.parse({ [field]: value });
        return null;
      } catch (error) {
        if (error instanceof z.ZodError) {
          const fieldError = error.errors.find(e => e.path.includes(field as string));
          return fieldError?.message || `Invalid ${field as string}`;
        }
        return `Validation error for ${field as string}`;
      }
    },
    [schema]
  );

  // Validate all fields
  const validateForm = useCallback((): boolean => {
    try {
      schema.parse(state.values);
      setState(prev => ({ ...prev, errors: [], isValid: true }));
      return true;
    } catch (error) {
      if (error instanceof z.ZodError) {
        const errors: ValidationError[] = error.errors.map(err => ({
          field: err.path.join('.'),
          message: err.message,
        }));
        setState(prev => ({ ...prev, errors, isValid: false }));
      }
      return false;
    }
  }, [schema, state.values]);

  // Update a single field value
  const setFieldValue = useCallback(
    (field: keyof T, value: any) => {
      setState(prev => ({
        ...prev,
        values: { ...prev.values, [field]: value },
      }));
    },
    []
  );

  // Mark a field as touched
  const setFieldTouched = useCallback(
    (field: keyof T, touched: boolean = true) => {
      setState(prev => {
        const newTouched = new Set(prev.touched);
        if (touched) {
          newTouched.add(field as string);
        } else {
          newTouched.delete(field as string);
        }
        return { ...prev, touched: newTouched };
      });
    },
    []
  );

  // Get error for a specific field
  const getFieldError = useCallback(
    (field: keyof T): string | null => {
      const error = state.errors.find(err => err.field === field);
      return error?.message || null;
    },
    [state.errors]
  );

  // Check if a field has been touched
  const isFieldTouched = useCallback(
    (field: keyof T): boolean => {
      return state.touched.has(field as string);
    },
    [state.touched]
  );

  // Check if a field has an error
  const hasFieldError = useCallback(
    (field: keyof T): boolean => {
      return getFieldError(field) !== null;
    },
    [getFieldError]
  );

  // Reset form to initial values
  const resetForm = useCallback(() => {
    setState({
      values: initialValues,
      errors: [],
      isValid: true,
      isSubmitting: false,
      touched: new Set(),
    });
  }, [initialValues]);

  // Set form as submitting
  const setSubmitting = useCallback((isSubmitting: boolean) => {
    setState(prev => ({ ...prev, isSubmitting }));
  }, []);

  // Handle form submission
  const handleSubmit = useCallback(
    async (onSubmit: (values: T) => Promise<void> | void) => {
      if (state.isSubmitting) return;

      setSubmitting(true);
      
      try {
        // Mark all fields as touched
        const allFields = Object.keys(state.values);
        allFields.forEach(field => setFieldTouched(field as keyof T, true));

        // Validate form
        if (!validateForm()) {
          return;
        }

        // Submit form
        await onSubmit(state.values);
      } catch (error) {
        console.error('Form submission error:', error);
        // Add generic error
        setState(prev => ({
          ...prev,
          errors: [
            ...prev.errors,
            { field: 'form', message: 'An error occurred while submitting the form' },
          ],
        }));
      } finally {
        setSubmitting(false);
      }
    },
    [state.isSubmitting, state.values, setSubmitting, setFieldTouched, validateForm]
  );

  // Update multiple fields at once
  const setValues = useCallback((values: Partial<T>) => {
    setState(prev => ({
      ...prev,
      values: { ...prev.values, ...values },
    }));
  }, []);

  return {
    // State
    values: state.values,
    errors: state.errors,
    isValid: state.isValid,
    isSubmitting: state.isSubmitting,
    touched: state.touched,
    
    // Actions
    setFieldValue,
    setFieldTouched,
    setValues,
    setSubmitting,
    resetForm,
    validateField,
    validateForm,
    
    // Helpers
    getFieldError,
    isFieldTouched,
    hasFieldError,
    handleSubmit,
  };
}





