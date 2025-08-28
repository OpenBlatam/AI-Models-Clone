import { useState, useCallback, useMemo } from 'react';

// ============================================================================
// TYPES
// ============================================================================

interface FormField {
  name: string;
  value: string;
  hasError: boolean;
  errorMessage: string;
  isTouched: boolean;
  isDirty: boolean;
}

interface FormValidation {
  isValid: boolean;
  hasErrors: boolean;
  errorCount: number;
  touchedCount: number;
  dirtyCount: number;
}

interface UseOptimizedFormReturn {
  formState: Record<string, FormField>;
  isSubmitting: boolean;
  isValidating: boolean;
  hasValidationErrors: boolean;
  isFormValid: boolean;
  hasUnsavedChanges: boolean;
  isAutoSaving: boolean;
  hasSubmissionError: boolean;
  shouldShowAllErrors: boolean;
  validateField: (fieldName: string) => void;
  validateForm: () => void;
  setFieldValue: (fieldName: string, value: string) => void;
  setFieldTouched: (fieldName: string, isTouched?: boolean) => void;
  setFieldError: (fieldName: string, errorMessage: string) => void;
  resetForm: () => void;
  handleSubmit: (onSubmit: (values: Record<string, string>) => void) => void;
}

// ============================================================================
// STATIC CONTENT
// ============================================================================

const DEFAULT_FIELD_STATE: Omit<FormField, 'name'> = {
  value: '',
  hasError: false,
  errorMessage: '',
  isTouched: false,
  isDirty: false,
};

const VALIDATION_RULES = {
  required: (value: string) => value.trim().length > 0 || 'This field is required',
  email: (value: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) || 'Invalid email format',
  minLength: (min: number) => (value: string) => value.length >= min || `Minimum ${min} characters required`,
  maxLength: (max: number) => (value: string) => value.length <= max || `Maximum ${max} characters allowed`,
  pattern: (regex: RegExp, message: string) => (value: string) => regex.test(value) || message,
};

// ============================================================================
// HELPERS
// ============================================================================

const createInitialFormState = (initialValues: Record<string, string>): Record<string, FormField> => {
  const formState: Record<string, FormField> = {};
  
  Object.keys(initialValues).forEach(fieldName => {
    formState[fieldName] = {
      name: fieldName,
      value: initialValues[fieldName] || '',
      hasError: false,
      errorMessage: '',
      isTouched: false,
      isDirty: false,
    };
  });
  
  return formState;
};

const validateFieldValue = (value: string, rules: any[]): { isValid: boolean; errorMessage: string } => {
  for (const rule of rules) {
    const result = rule(value);
    if (result !== true) {
      return { isValid: false, errorMessage: result };
    }
  }
  return { isValid: true, errorMessage: '' };
};

const calculateFormValidation = (formState: Record<string, FormField>): FormValidation => {
  const fields = Object.values(formState);
  const hasErrors = fields.some(field => field.hasError);
  const errorCount = fields.filter(field => field.hasError).length;
  const touchedCount = fields.filter(field => field.isTouched).length;
  const dirtyCount = fields.filter(field => field.isDirty).length;
  const isValid = !hasErrors && fields.every(field => field.value.trim().length > 0);
  
  return {
    isValid,
    hasErrors,
    errorCount,
    touchedCount,
    dirtyCount,
  };
};

// ============================================================================
// MAIN EXPORTED HOOK
// ============================================================================

export const useOptimizedForm = (
  initialValues: Record<string, string> = {},
  validationRules: Record<string, any[]> = {}
): UseOptimizedFormReturn => {
  // State management with descriptive names
  const [formState, setFormState] = useState<Record<string, FormField>>(() => 
    createInitialFormState(initialValues)
  );
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isValidating, setIsValidating] = useState(false);
  const [hasSubmissionError, setHasSubmissionError] = useState(false);
  const [shouldShowAllErrors, setShouldShowAllErrors] = useState(false);

  // Memoized validation state
  const formValidation = useMemo(() => calculateFormValidation(formState), [formState]);
  
  const hasValidationErrors = formValidation.hasErrors;
  const isFormValid = formValidation.isValid;
  const hasUnsavedChanges = formValidation.dirtyCount > 0;
  const isAutoSaving = false; // Placeholder for auto-save functionality

  // Field validation
  const validateField = useCallback((fieldName: string) => {
    const field = formState[fieldName];
    if (!field) return;

    const rules = validationRules[fieldName] || [];
    const { isValid, errorMessage } = validateFieldValue(field.value, rules);

    setFormState(prev => ({
      ...prev,
      [fieldName]: {
        ...prev[fieldName],
        hasError: !isValid,
        errorMessage: errorMessage,
      },
    }));
  }, [formState, validationRules]);

  // Form validation
  const validateForm = useCallback(() => {
    setIsValidating(true);
    
    Object.keys(formState).forEach(fieldName => {
      validateField(fieldName);
    });
    
    setIsValidating(false);
    setShouldShowAllErrors(true);
  }, [formState, validateField]);

  // Field value setter
  const setFieldValue = useCallback((fieldName: string, value: string) => {
    setFormState(prev => {
      const currentField = prev[fieldName];
      if (!currentField) return prev;

      const isDirty = value !== initialValues[fieldName];
      
      return {
        ...prev,
        [fieldName]: {
          ...currentField,
          value,
          isDirty,
          hasError: false, // Clear error when user types
          errorMessage: '',
        },
      };
    });
  }, [initialValues]);

  // Field touched setter
  const setFieldTouched = useCallback((fieldName: string, isTouched: boolean = true) => {
    setFormState(prev => {
      const currentField = prev[fieldName];
      if (!currentField) return prev;

      return {
        ...prev,
        [fieldName]: {
          ...currentField,
          isTouched,
        },
      };
    });
  }, []);

  // Field error setter
  const setFieldError = useCallback((fieldName: string, errorMessage: string) => {
    setFormState(prev => {
      const currentField = prev[fieldName];
      if (!currentField) return prev;

      return {
        ...prev,
        [fieldName]: {
          ...currentField,
          hasError: true,
          errorMessage,
        },
      };
    });
  }, []);

  // Form reset
  const resetForm = useCallback(() => {
    setFormState(createInitialFormState(initialValues));
    setIsSubmitting(false);
    setIsValidating(false);
    setHasSubmissionError(false);
    setShouldShowAllErrors(false);
  }, [initialValues]);

  // Form submission
  const handleSubmit = useCallback((onSubmit: (values: Record<string, string>) => void) => {
    validateForm();
    
    if (!isFormValid) {
      setHasSubmissionError(true);
      return;
    }

    setIsSubmitting(true);
    setHasSubmissionError(false);

    try {
      const values = Object.keys(formState).reduce((acc, fieldName) => {
        acc[fieldName] = formState[fieldName].value;
        return acc;
      }, {} as Record<string, string>);

      onSubmit(values);
    } catch (error) {
      setHasSubmissionError(true);
    } finally {
      setIsSubmitting(false);
    }
  }, [formState, isFormValid, validateForm]);

  return {
    formState,
    isSubmitting,
    isValidating,
    hasValidationErrors,
    isFormValid,
    hasUnsavedChanges,
    isAutoSaving,
    hasSubmissionError,
    shouldShowAllErrors,
    validateField,
    validateForm,
    setFieldValue,
    setFieldTouched,
    setFieldError,
    resetForm,
    handleSubmit,
  };
}; 