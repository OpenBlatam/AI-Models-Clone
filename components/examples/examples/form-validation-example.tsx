'use client';

import React, { useState, useCallback, useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { useFormValidation } from '@/hooks/use-form-validation';
import { z } from 'zod';
import { toast } from 'react-hot-toast';
import { Save, RefreshCw, AlertCircle, CheckCircle } from 'lucide-react';

// Schema definition for better type safety
const userSchema = z.object({
  name: z.string()
    .min(2, 'Name must be at least 2 characters')
    .max(50, 'Name must be less than 50 characters'),
  email: z.string()
    .email('Invalid email address')
    .min(5, 'Email must be at least 5 characters'),
  role: z.string()
    .min(1, 'Role is required')
    .max(30, 'Role must be less than 30 characters'),
});

type UserFormData = z.infer<typeof userSchema>;

// Constants for better maintainability
const INITIAL_VALUES: UserFormData = {
  name: '',
  email: '',
  role: '',
};

const FIELD_CONFIG = [
  { key: 'name' as const, label: 'Name', placeholder: 'Enter name' },
  { key: 'email' as const, label: 'Email', placeholder: 'Enter email' },
  { key: 'role' as const, label: 'Role', placeholder: 'Enter role' },
] as const;

interface ValidationStatus {
  isValid: boolean;
  hasErrors: boolean;
  touchedCount: number;
  errorCount: number;
}

export default function FormValidationExample() {
  // Form validation hook
  const {
    values,
    errors,
    isValid,
    isSubmitting,
    touched,
    setFieldValue,
    setFieldTouched,
    getFieldError,
    isFieldTouched,
    hasFieldError,
    handleSubmit,
    resetForm,
  } = useFormValidation(userSchema, INITIAL_VALUES);

  // Local state for UI feedback
  const [showSuccess, setShowSuccess] = useState(false);

  // Memoized computed values
  const validationStatus: ValidationStatus = useMemo(() => ({
    isValid,
    hasErrors: errors.length > 0,
    touchedCount: touched.size,
    errorCount: errors.length,
  }), [isValid, errors.length, touched.size]);

  const formProgress = useMemo(() => {
    const totalFields = FIELD_CONFIG.length;
    const completedFields = FIELD_CONFIG.filter(field => 
      values[field.key] && !hasFieldError(field.key)
    ).length;
    return Math.round((completedFields / totalFields) * 100);
  }, [values, hasFieldError]);

  // Optimized handlers with useCallback
  const handleFieldChange = useCallback((field: keyof UserFormData, value: string) => {
    try {
      setFieldValue(field, value);
    } catch (error) {
      console.error('Field change error:', error);
    }
  }, [setFieldValue]);

  const handleFieldBlur = useCallback((field: keyof UserFormData) => {
    try {
      setFieldTouched(field);
    } catch (error) {
      console.error('Field blur error:', error);
    }
  }, [setFieldTouched]);

  const onSubmit = useCallback(async (data: UserFormData) => {
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      toast.success(`User ${data.name} saved successfully!`);
      console.log('Form submitted:', data);
      resetForm();
      setShowSuccess(true);
      setTimeout(() => setShowSuccess(false), 3000);
    } catch (error) {
      toast.error('Failed to save user. Please try again.');
      console.error('Form submission error:', error);
    }
  }, [resetForm]);

  const handleReset = useCallback(() => {
    try {
      resetForm();
      toast.success('Form reset successfully!');
    } catch (error) {
      toast.error('Failed to reset form');
      console.error('Form reset error:', error);
    }
  }, [resetForm]);

  // Early return for invalid states
  if (!values || !errors) {
    return (
      <div className="text-center py-8">
        <p className="text-destructive">Failed to initialize form</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Form Card */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Form</CardTitle>
            <CardDescription>
              Interactive form with real-time validation
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Progress Bar */}
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Form Progress</span>
                <span>{formProgress}%</span>
              </div>
              <div className="w-full bg-muted rounded-full h-2">
                <div 
                  className="bg-primary h-2 rounded-full transition-all duration-300"
                  style={{ width: `${formProgress}%` }}
                />
              </div>
            </div>

            {/* Form Fields */}
            {FIELD_CONFIG.map((field) => (
              <div key={field.key} className="space-y-2">
                <label className="text-sm font-medium flex items-center gap-2">
                  {field.label}
                  {isFieldTouched(field.key) && hasFieldError(field.key) && (
                    <AlertCircle className="h-4 w-4 text-destructive" />
                  )}
                  {isFieldTouched(field.key) && !hasFieldError(field.key) && values[field.key] && (
                    <CheckCircle className="h-4 w-4 text-green-600" />
                  )}
                </label>
                <Input
                  placeholder={field.placeholder}
                  value={values[field.key]}
                  onChange={(e) => handleFieldChange(field.key, e.target.value)}
                  onBlur={() => handleFieldBlur(field.key)}
                  className={`transition-all duration-200 ${
                    hasFieldError(field.key) && isFieldTouched(field.key)
                      ? 'border-destructive ring-1 ring-destructive'
                      : isFieldTouched(field.key) && values[field.key] && !hasFieldError(field.key)
                      ? 'border-green-500 ring-1 ring-green-500'
                      : ''
                  }`}
                />
                {hasFieldError(field.key) && isFieldTouched(field.key) && (
                  <p className="text-sm text-destructive flex items-center gap-1">
                    <AlertCircle className="h-3 w-3" />
                    {getFieldError(field.key)}
                  </p>
                )}
              </div>
            ))}

            {/* Form Actions */}
            <div className="flex gap-2 pt-2">
              <Button 
                onClick={() => handleSubmit(onSubmit)}
                disabled={!isValid || isSubmitting}
                className="flex-1"
              >
                {isSubmitting ? (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="h-4 w-4 mr-2" />
                    Save User
                  </>
                )}
              </Button>
              <Button variant="outline" onClick={handleReset}>
                Reset
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Form State Card */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Form State</CardTitle>
            <CardDescription>
              Real-time form validation status
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Status Badges */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Badge variant={validationStatus.isValid ? 'success' : 'destructive'}>
                  {validationStatus.isValid ? 'Valid' : 'Invalid'}
                </Badge>
                <Badge variant={isSubmitting ? 'default' : 'secondary'}>
                  {isSubmitting ? 'Submitting' : 'Ready'}
                </Badge>
                {validationStatus.hasErrors && (
                  <Badge variant="destructive">
                    {validationStatus.errorCount} Errors
                  </Badge>
                )}
              </div>
            </div>

            {/* Field Status */}
            <div className="space-y-2">
              <h4 className="font-medium">Field Status:</h4>
              {FIELD_CONFIG.map((field) => (
                <div key={field.key} className="flex items-center gap-2 text-sm">
                  <Badge 
                    variant={isFieldTouched(field.key) ? 'default' : 'secondary'} 
                    size="sm"
                  >
                    {field.key}
                  </Badge>
                  <span className={isFieldTouched(field.key) ? 'text-foreground' : 'text-muted-foreground'}>
                    {isFieldTouched(field.key) ? 'Touched' : 'Untouched'}
                  </span>
                  {hasFieldError(field.key) && (
                    <Badge variant="destructive" size="sm">
                      Error
                    </Badge>
                  )}
                  {isFieldTouched(field.key) && !hasFieldError(field.key) && values[field.key] && (
                    <Badge variant="success" size="sm">
                      Valid
                    </Badge>
                  )}
                </div>
              ))}
            </div>

            {/* Form Statistics */}
            <div className="space-y-2">
              <h4 className="font-medium">Form Statistics:</h4>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="bg-muted p-2 rounded">
                  <p className="font-medium">Touched Fields</p>
                  <p className="text-muted-foreground">{validationStatus.touchedCount}/{FIELD_CONFIG.length}</p>
                </div>
                <div className="bg-muted p-2 rounded">
                  <p className="font-medium">Errors</p>
                  <p className="text-muted-foreground">{validationStatus.errorCount}</p>
                </div>
              </div>
            </div>

            {/* Current Values */}
            <div className="space-y-2">
              <h4 className="font-medium">Current Values:</h4>
              <pre className="text-xs bg-muted p-2 rounded overflow-auto">
                {JSON.stringify(values, null, 2)}
              </pre>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Success Message */}
      {showSuccess && (
        <div className="flex items-center gap-2 p-4 bg-green-50 border border-green-200 rounded-lg">
          <CheckCircle className="h-5 w-5 text-green-600" />
          <span className="text-sm text-green-800">
            Form submitted successfully! The form has been reset.
          </span>
        </div>
      )}

      {/* Validation Tips */}
      <div className="text-sm text-muted-foreground space-y-2">
        <p>💡 This demonstrates real-time validation with Zod schemas and field-level validation!</p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div className="bg-muted p-3 rounded-lg">
            <p className="font-medium mb-1">Validation Features</p>
            <ul className="space-y-1">
              <li>• Real-time validation</li>
              <li>• Field-level errors</li>
              <li>• Touch state tracking</li>
            </ul>
          </div>
          <div className="bg-muted p-3 rounded-lg">
            <p className="font-medium mb-1">Schema Benefits</p>
            <ul className="space-y-1">
              <li>• Type safety</li>
              <li>• Runtime validation</li>
              <li>• Custom error messages</li>
            </ul>
          </div>
          <div className="bg-muted p-3 rounded-lg">
            <p className="font-medium mb-1">User Experience</p>
            <ul className="space-y-1">
              <li>• Visual feedback</li>
              <li>• Progress tracking</li>
              <li>• Clear error messages</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}





