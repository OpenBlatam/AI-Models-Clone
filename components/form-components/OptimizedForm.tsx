import React, { useState, useCallback, useMemo } from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { OptimizedInput } from './OptimizedInput';
import { OptimizedButton } from './OptimizedButton';
import { OptimizedIcon } from './OptimizedIcon';

interface FormField {
  name: string;
  label: string;
  type: 'text' | 'email' | 'password' | 'number' | 'textarea';
  placeholder?: string;
  isRequired?: boolean;
  validationRules?: ((value: any) => string | null)[];
  defaultValue?: string;
}

interface FormValidation {
  isValid: boolean;
  errors: Record<string, string[]>;
  touchedFields: Record<string, boolean>;
}

interface OptimizedFormProps {
  fields: FormField[];
  onSubmit: (values: Record<string, any>) => void;
  onCancel?: () => void;
  submitButtonText?: string;
  cancelButtonText?: string;
  isSubmitting?: boolean;
  hasValidationErrors?: boolean;
  shouldShowValidationOnBlur?: boolean;
  shouldShowValidationOnChange?: boolean;
  canAutoFocus?: boolean;
  hasAutoSave?: boolean;
  autoSaveDelay?: number;
}

export const OptimizedForm: React.FC<OptimizedFormProps> = ({
  fields,
  onSubmit,
  onCancel,
  submitButtonText = 'Submit',
  cancelButtonText = 'Cancel',
  isSubmitting = false,
  hasValidationErrors = false,
  shouldShowValidationOnBlur = true,
  shouldShowValidationOnChange = false,
  canAutoFocus = false,
  hasAutoSave = false,
  autoSaveDelay = 2000,
}) => {
  // Form state with descriptive variable names
  const [formValues, setFormValues] = useState<Record<string, any>>({});
  const [hasTouchedFields, setHasTouchedFields] = useState<Record<string, boolean>>({});
  const [hasValidationErrors, setHasValidationErrors] = useState<Record<string, string[]>>({});
  const [isFormValid, setIsFormValid] = useState<boolean>(true);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState<boolean>(false);
  const [isAutoSaving, setIsAutoSaving] = useState<boolean>(false);
  const [hasSubmissionError, setHasSubmissionError] = useState<boolean>(false);
  const [shouldShowAllErrors, setShouldShowAllErrors] = useState<boolean>(false);

  // Initialize form values with descriptive names
  const initializeFormValues = useCallback(() => {
    const initialValues: Record<string, any> = {};
    fields.forEach(field => {
      initialValues[field.name] = field.defaultValue || '';
    });
    setFormValues(initialValues);
  }, [fields]);

  // Validate field with descriptive function name
  const validateField = useCallback((fieldName: string, value: any): string[] => {
    const field = fields.find(f => f.name === fieldName);
    if (!field || !field.validationRules) return [];

    const errors: string[] = [];
    field.validationRules.forEach(rule => {
      const error = rule(value);
      if (error) errors.push(error);
    });

    return errors;
  }, [fields]);

  // Validate entire form with descriptive function name
  const validateForm = useCallback((): FormValidation => {
    const errors: Record<string, string[]> = {};
    const touchedFields: Record<string, boolean> = {};
    let isValid = true;

    fields.forEach(field => {
      const fieldErrors = validateField(field.name, formValues[field.name] || '');
      if (fieldErrors.length > 0) {
        errors[field.name] = fieldErrors;
        isValid = false;
      }
      touchedFields[field.name] = hasTouchedFields[field.name] || false;
    });

    return { isValid, errors, touchedFields };
  }, [fields, formValues, hasTouchedFields, validateField]);

  // Handle field value change with descriptive function name
  const handleFieldValueChange = useCallback((fieldName: string, value: any) => {
    setFormValues(prev => ({ ...prev, [fieldName]: value }));
    setHasUnsavedChanges(true);

    if (shouldShowValidationOnChange) {
      const fieldErrors = validateField(fieldName, value);
      setHasValidationErrors(prev => ({ ...prev, [fieldName]: fieldErrors }));
    }
  }, [shouldShowValidationOnChange, validateField]);

  // Handle field blur with descriptive function name
  const handleFieldBlur = useCallback((fieldName: string) => {
    setHasTouchedFields(prev => ({ ...prev, [fieldName]: true }));
    
    if (shouldShowValidationOnBlur) {
      const fieldErrors = validateField(fieldName, formValues[fieldName] || '');
      setHasValidationErrors(prev => ({ ...prev, [fieldName]: fieldErrors }));
    }
  }, [shouldShowValidationOnBlur, validateField, formValues]);

  // Handle form submission with descriptive function name
  const handleFormSubmission = useCallback(() => {
    const validation = validateForm();
    setShouldShowAllErrors(true);
    setHasValidationErrors(validation.errors);
    setHasTouchedFields(validation.touchedFields);

    if (validation.isValid) {
      setHasSubmissionError(false);
      onSubmit(formValues);
    } else {
      setHasSubmissionError(true);
    }
  }, [validateForm, formValues, onSubmit]);

  // Handle form cancellation with descriptive function name
  const handleFormCancellation = useCallback(() => {
    if (hasUnsavedChanges) {
      // Could show confirmation dialog here
      setHasUnsavedChanges(false);
    }
    onCancel?.();
  }, [hasUnsavedChanges, onCancel]);

  // Auto-save functionality with descriptive function name
  const handleAutoSave = useCallback(() => {
    if (hasAutoSave && hasUnsavedChanges && isFormValid) {
      setIsAutoSaving(true);
      // Simulate auto-save
      setTimeout(() => {
        setIsAutoSaving(false);
        setHasUnsavedChanges(false);
      }, 1000);
    }
  }, [hasAutoSave, hasUnsavedChanges, isFormValid]);

  // Memoized form validation state
  const formValidation = useMemo(() => validateForm(), [validateForm]);

  // Memoized field rendering with descriptive names
  const renderFormFields = useMemo(() => {
    return fields.map((field, index) => {
      const fieldValue = formValues[field.name] || '';
      const hasFieldErrors = hasValidationErrors[field.name]?.length > 0;
      const hasFieldBeenTouched = hasTouchedFields[field.name];
      const shouldShowFieldErrors = shouldShowAllErrors || hasFieldBeenTouched;
      const fieldErrors = shouldShowFieldErrors ? hasValidationErrors[field.name] || [] : [];

      return (
        <View key={field.name} style={styles.fieldContainer}>
          <OptimizedInput
            label={field.label}
            placeholder={field.placeholder}
            value={fieldValue}
            onChangeText={(value) => handleFieldValueChange(field.name, value)}
            onBlur={() => handleFieldBlur(field.name)}
            error={fieldErrors[0]}
            isRequired={field.isRequired}
            secureTextEntry={field.type === 'password'}
            keyboardType={field.type === 'email' ? 'email-address' : field.type === 'number' ? 'numeric' : 'default'}
            autoFocus={canAutoFocus && index === 0}
            leftIcon={field.isRequired ? { name: 'star', color: '#FF3B30' } : undefined}
          />
        </View>
      );
    });
  }, [
    fields,
    formValues,
    hasValidationErrors,
    hasTouchedFields,
    shouldShowAllErrors,
    handleFieldValueChange,
    handleFieldBlur,
    canAutoFocus,
  ]);

  // Memoized action buttons with descriptive names
  const renderActionButtons = useMemo(() => {
    const canSubmit = formValidation.isValid && !isSubmitting;
    const hasCancelAction = !!onCancel;

    return (
      <View style={styles.buttonContainer}>
        {hasCancelAction && (
          <OptimizedButton
            title={cancelButtonText}
            onPress={handleFormCancellation}
            variant="outline"
            isDisabled={isSubmitting}
            style={styles.cancelButton}
          />
        )}
        <OptimizedButton
          title={submitButtonText}
          onPress={handleFormSubmission}
          isLoading={isSubmitting}
          isDisabled={!canSubmit}
          style={styles.submitButton}
        />
      </View>
    );
  }, [
    formValidation.isValid,
    isSubmitting,
    submitButtonText,
    cancelButtonText,
    onCancel,
    handleFormSubmission,
    handleFormCancellation,
  ]);

  // Memoized status indicators with descriptive names
  const renderStatusIndicators = useMemo(() => {
    const hasErrors = Object.keys(hasValidationErrors).length > 0;
    const hasAutoSaveIndicator = hasAutoSave && isAutoSaving;
    const hasUnsavedChangesIndicator = hasUnsavedChanges && !isAutoSaving;

    return (
      <View style={styles.statusContainer}>
        {hasErrors && (
          <View style={styles.errorIndicator}>
            <OptimizedIcon name="warning" size="small" variant="error" />
            <Text style={styles.errorText}>Please fix the errors above</Text>
          </View>
        )}
        {hasAutoSaveIndicator && (
          <View style={styles.autoSaveIndicator}>
            <OptimizedIcon name="save" size="small" variant="info" />
            <Text style={styles.autoSaveText}>Auto-saving...</Text>
          </View>
        )}
        {hasUnsavedChangesIndicator && (
          <View style={styles.unsavedChangesIndicator}>
            <OptimizedIcon name="information-circle" size="small" variant="warning" />
            <Text style={styles.unsavedChangesText}>Unsaved changes</Text>
          </View>
        )}
      </View>
    );
  }, [
    hasValidationErrors,
    hasAutoSave,
    isAutoSaving,
    hasUnsavedChanges,
  ]);

  // Initialize form on mount
  React.useEffect(() => {
    initializeFormValues();
  }, [initializeFormValues]);

  // Auto-save effect
  React.useEffect(() => {
    if (hasAutoSave && hasUnsavedChanges) {
      const timeoutId = setTimeout(handleAutoSave, autoSaveDelay);
      return () => clearTimeout(timeoutId);
    }
  }, [hasAutoSave, hasUnsavedChanges, handleAutoSave, autoSaveDelay]);

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <View style={styles.formContainer}>
        {renderFormFields}
        {renderStatusIndicators}
        {renderActionButtons}
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  formContainer: {
    padding: 16,
  },
  fieldContainer: {
    marginBottom: 16,
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 24,
    gap: 12,
  },
  submitButton: {
    flex: 1,
  },
  cancelButton: {
    flex: 1,
  },
  statusContainer: {
    marginTop: 16,
    gap: 8,
  },
  errorIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    backgroundColor: '#FFE5E5',
    borderRadius: 8,
    gap: 8,
  },
  errorText: {
    fontSize: 14,
    color: '#FF3B30',
    fontWeight: '500',
  },
  autoSaveIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    backgroundColor: '#E5F3FF',
    borderRadius: 8,
    gap: 8,
  },
  autoSaveText: {
    fontSize: 14,
    color: '#007AFF',
    fontWeight: '500',
  },
  unsavedChangesIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    backgroundColor: '#FFF8E5',
    borderRadius: 8,
    gap: 8,
  },
  unsavedChangesText: {
    fontSize: 14,
    color: '#FF9500',
    fontWeight: '500',
  },
}); 