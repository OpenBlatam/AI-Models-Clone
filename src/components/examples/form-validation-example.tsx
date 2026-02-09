'use client';

import React, { useState, useCallback, useMemo, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { useFormValidation } from '@/hooks/use-form-validation';
import { z } from 'zod';
import { toast } from 'react-hot-toast';
import { Save, RefreshCw, AlertCircle, CheckCircle, Info, AlertTriangle, User, Mail, Phone, MapPin } from 'lucide-react';
import { usePerformanceMonitor, useHookStatusMonitor, useExamplesStore } from '@/lib/stores/examples-store';

const userSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters').max(50, 'Name must be less than 50 characters'),
  email: z.string().email('Please enter a valid email address'),
  phone: z.string().regex(/^\+?[\d\s\-\(\)]+$/, 'Please enter a valid phone number'),
  address: z.string().min(10, 'Address must be at least 10 characters').max(200, 'Address must be less than 200 characters'),
  city: z.string().min(2, 'City must be at least 2 characters').max(50, 'City must be less than 50 characters'),
  zipCode: z.string().regex(/^\d{5}(-\d{4})?$/, 'Please enter a valid ZIP code')
});

type UserFormData = z.infer<typeof userSchema>;

const INITIAL_VALUES: UserFormData = {
  name: '',
  email: '',
  phone: '',
  address: '',
  city: '',
  zipCode: ''
};

const FIELD_CONFIG = [
  { key: 'name', label: 'Full Name', icon: User, placeholder: 'Enter your full name' },
  { key: 'email', label: 'Email Address', icon: Mail, placeholder: 'Enter your email address' },
  { key: 'phone', label: 'Phone Number', icon: Phone, placeholder: 'Enter your phone number' },
  { key: 'address', label: 'Street Address', icon: MapPin, placeholder: 'Enter your street address' },
  { key: 'city', label: 'City', icon: MapPin, placeholder: 'Enter your city' },
  { key: 'zipCode', label: 'ZIP Code', icon: MapPin, placeholder: 'Enter your ZIP code' }
] as const;

interface ValidationStatus {
  isValid: boolean;
  touchedFields: number;
  errorCount: number;
  progress: number;
}

export default function FormValidationExample() {
  const [showSuccess, setShowSuccess] = useState(false);

  // Performance monitoring
  const { updatePerformanceMetrics } = usePerformanceMonitor();
  const { updateHookStatus } = useHookStatusMonitor('formValidation');

  // Form validation hook
  const {
    values,
    errors,
    touched,
    isValid,
    isSubmitting,
    handleChange,
    handleBlur,
    handleSubmit,
    resetForm,
    setFieldValue
  } = useFormValidation({
    initialValues: INITIAL_VALUES,
    validationSchema: userSchema,
    onSubmit: async (data) => {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      return { success: true, data };
    }
  });

  // Error handling
  const [hasError, setHasError] = useState(false);

  // Memoized validation status
  const validationStatus = useMemo((): ValidationStatus => {
    const touchedFields = Object.values(touched).filter(Boolean).length;
    const errorCount = Object.keys(errors).length;
    const progress = Math.round((touchedFields / Object.keys(INITIAL_VALUES).length) * 100);
    
    return {
      isValid,
      touchedFields,
      errorCount,
      progress
    };
  }, [touched, errors, isValid]);

  // Form progress calculation
  const formProgress = useMemo(() => {
    const totalFields = Object.keys(INITIAL_VALUES).length;
    const completedFields = Object.values(values).filter(value => value.trim() !== '').length;
    return Math.round((completedFields / totalFields) * 100);
  }, [values]);

  // Update hook status in store
  useEffect(() => {
    try {
      updateHookStatus({
        isActive: Object.values(touched).some(Boolean),
        lastUsed: Date.now(),
        usageCount: (prev) => prev + 1
      });
    } catch (error) {
      console.error('Failed to update hook status:', error);
      setHasError(true);
    }
  }, [touched, updateHookStatus]);

  // Log errors to store
  useEffect(() => {
    if (hasError) {
      const { logError } = useExamplesStore.getState();
      logError({
        message: 'Form validation error',
        stack: 'Error in form validation example component',
        severity: 'warning'
      });
    }
  }, [hasError]);

  // Handle field changes with error handling
  const handleFieldChange = useCallback((field: keyof UserFormData, value: string) => {
    try {
      handleChange(field, value);
    } catch (error) {
      console.error('Field change error:', error);
      setHasError(true);
      toast.error('Failed to update field');
    }
  }, [handleChange]);

  // Handle field blur with error handling
  const handleFieldBlur = useCallback((field: keyof UserFormData) => {
    try {
      handleBlur(field);
    } catch (error) {
      console.error('Field blur error:', error);
      setHasError(true);
      toast.error('Failed to validate field');
    }
  }, [handleBlur]);

  // Handle form submission with error handling
  const onSubmit = useCallback(async (data: UserFormData) => {
    try {
      const result = await handleSubmit(data);
      if (result?.success) {
        toast.success('User saved successfully!');
        resetForm();
        setShowSuccess(true);
        setTimeout(() => setShowSuccess(false), 5000);
      }
    } catch (error) {
      console.error('Form submission error:', error);
      setHasError(true);
      toast.error('Failed to save user');
    }
  }, [handleSubmit, resetForm]);

  // Handle form reset with error handling
  const handleReset = useCallback(() => {
    try {
      resetForm();
      setShowSuccess(false);
      toast.success('Form reset successfully');
    } catch (error) {
      console.error('Form reset error:', error);
      setHasError(true);
      toast.error('Failed to reset form');
    }
  }, [resetForm]);

  // Early return for initialization failures
  if (hasError) {
    return (
      <Card className="border-destructive">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-destructive">
            <AlertTriangle className="h-5 w-5" />
            Error Loading Component
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            There was an error initializing the form validation example. Please refresh the page.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Form Progress */}
      {formProgress > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Form Progress</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Completion</span>
                <span>{formProgress}%</span>
              </div>
              <div className="w-full bg-muted rounded-full h-2">
                <div 
                  className="bg-primary h-2 rounded-full transition-all duration-300"
                  style={{ width: `${formProgress}%` }}
                />
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Form Inputs */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">User Information</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {FIELD_CONFIG.map(({ key, label, icon: Icon, placeholder }) => (
              <div key={key} className="space-y-2">
                <label htmlFor={key} className="text-sm font-medium flex items-center gap-2">
                  <Icon className="h-4 w-4" />
                  {label}
                </label>
                <Input
                  id={key}
                  type={key === 'email' ? 'email' : 'text'}
                  placeholder={placeholder}
                  value={values[key]}
                  onChange={(e) => handleFieldChange(key, e.target.value)}
                  onBlur={() => handleFieldBlur(key)}
                  className={`transition-all duration-200 ${
                    touched[key] && errors[key] 
                      ? 'border-destructive ring-1 ring-destructive' 
                      : touched[key] && !errors[key]
                      ? 'border-green-500 ring-1 ring-green-500'
                      : ''
                  }`}
                  aria-describedby={`${key}-help`}
                  aria-invalid={touched[key] && !!errors[key]}
                  data-testid={`${key}-input`}
                />
                {touched[key] && errors[key] && (
                  <div className="flex items-center gap-2 text-sm text-destructive">
                    <AlertCircle className="h-4 w-4" />
                    {errors[key]}
                  </div>
                )}
                {touched[key] && !errors[key] && (
                  <div className="flex items-center gap-2 text-sm text-green-600">
                    <CheckCircle className="h-4 w-4" />
                    Valid
                  </div>
                )}
                <p id={`${key}-help`} className="text-xs text-muted-foreground">
                  {key === 'name' && 'Enter your full legal name'}
                  {key === 'email' && 'We\'ll never share your email'}
                  {key === 'phone' && 'Include country code if international'}
                  {key === 'address' && 'Full street address including apartment/unit'}
                  {key === 'city' && 'City or town name'}
                  {key === 'zipCode' && '5-digit ZIP code or ZIP+4 format'}
                </p>
              </div>
            ))}
          </div>

          {/* Form Actions */}
          <div className="flex flex-wrap gap-3 pt-4">
            <Button 
              onClick={() => onSubmit(values)}
              disabled={!isValid || isSubmitting}
              className="min-w-[120px]"
              data-testid="save-user-button"
              aria-label="Save user information"
            >
              {isSubmitting ? (
                <>
                  <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="mr-2 h-4 w-4" />
                  Save User
                </>
              )}
            </Button>
            <Button 
              variant="outline" 
              onClick={handleReset}
              disabled={isSubmitting}
              data-testid="reset-form-button"
              aria-label="Reset form to initial values"
            >
              <RefreshCw className="mr-2 h-4 w-4" />
              Reset Form
            </Button>
          </div>

          {/* Success Message */}
          {showSuccess && (
            <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center gap-2 text-green-800">
                <CheckCircle className="h-5 w-5" />
                <span className="font-medium">User saved successfully!</span>
              </div>
              <p className="text-sm text-green-600 mt-1">
                The form has been reset and is ready for new input.
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Form State */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Form State</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">Form Status:</span>
                <Badge variant={isValid ? 'default' : 'destructive'}>
                  {isValid ? 'Valid' : 'Invalid'}
                </Badge>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">Submission:</span>
                <Badge variant={isSubmitting ? 'default' : 'secondary'}>
                  {isSubmitting ? 'Submitting' : 'Ready'}
                </Badge>
              </div>
            </div>
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">Touched Fields:</span>
                <Badge variant="outline">
                  {validationStatus.touchedFields} / {Object.keys(INITIAL_VALUES).length}
                </Badge>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">Errors:</span>
                <Badge variant={validationStatus.errorCount > 0 ? 'destructive' : 'default'}>
                  {validationStatus.errorCount}
                </Badge>
              </div>
            </div>
          </div>

          {/* Field Status Grid */}
          <div className="space-y-2">
            <h4 className="font-medium text-sm">Field Status</h4>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
              {FIELD_CONFIG.map(({ key, label }) => (
                <div key={key} className="flex items-center gap-2 text-xs">
                  <Badge 
                    variant={touched[key] ? (errors[key] ? 'destructive' : 'default') : 'secondary'}
                    className="text-xs"
                  >
                    {touched[key] ? (errors[key] ? 'Error' : 'Valid') : 'Untouched'}
                  </Badge>
                  <span className="text-muted-foreground">{label}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Current Values */}
          <div className="space-y-2">
            <h4 className="font-medium text-sm">Current Values</h4>
            <pre className="text-xs bg-muted p-3 rounded overflow-auto max-h-32">
              {JSON.stringify(values, null, 2)}
            </pre>
          </div>
        </CardContent>
      </Card>

      {/* Validation Tips */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Info className="h-5 w-5" />
            Validation Benefits
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="space-y-2">
            <h4 className="font-medium">Schema Validation</h4>
            <ul className="text-sm text-muted-foreground space-y-1">
              <li>• Type-safe validation with Zod schemas</li>
              <li>• Automatic error messages and localization</li>
              <li>• Complex validation rules and transformations</li>
              <li>• Runtime type checking and inference</li>
            </ul>
          </div>
          <div className="space-y-2">
            <h4 className="font-medium">User Experience</h4>
            <ul className="text-sm text-muted-foreground space-y-1">
              <li>• Real-time validation feedback</li>
              <li>• Clear error messages and visual indicators</li>
              <li>• Form progress tracking</li>
              <li>• Accessible form controls</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}





