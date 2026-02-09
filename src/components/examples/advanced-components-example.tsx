'use client';

import React, { useState, useCallback, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { AdvancedButton } from '@/components/ui/advanced-button';
import { AdvancedInput } from '@/components/ui/advanced-input';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { usePerformanceMonitor, useHookStatusMonitor } from '@/lib/stores/examples-store';
import { useExamplesStore } from '@/lib/stores/examples-store';
import { toast } from 'react-hot-toast';
import { 
  User, 
  Mail, 
  Lock, 
  Phone, 
  MapPin, 
  Star, 
  Heart, 
  Zap, 
  Settings, 
  Download,
  Upload,
  Play,
  Pause,
  Stop,
  CheckCircle
} from 'lucide-react';

// Validation rules for the advanced inputs
const emailValidation = [
  {
    test: (value: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value),
    message: 'Please enter a valid email address',
    severity: 'error' as const,
  },
  {
    test: (value: string) => value.length >= 5,
    message: 'Email must be at least 5 characters',
    severity: 'warning' as const,
  },
];

const passwordValidation = [
  {
    test: (value: string) => value.length >= 8,
    message: 'Password must be at least 8 characters',
    severity: 'error' as const,
  },
  {
    test: (value: string) => /[A-Z]/.test(value),
    message: 'Password must contain at least one uppercase letter',
    severity: 'error' as const,
  },
  {
    test: (value: string) => /[0-9]/.test(value),
    message: 'Password must contain at least one number',
    severity: 'error' as const,
  },
  {
    test: (value: string) => /[^A-Za-z0-9]/.test(value),
    message: 'Password must contain at least one special character',
    severity: 'warning' as const,
  },
];

const phoneValidation = [
  {
    test: (value: string) => /^[\+]?[1-9][\d]{0,15}$/.test(value.replace(/\s/g, '')),
    message: 'Please enter a valid phone number',
    severity: 'error' as const,
  },
];

export default function AdvancedComponentsExample() {
  // Performance monitoring
  const { measureRenderTime, measureMemoryUsage } = usePerformanceMonitor();
  const { updateHookStatus } = useHookStatusMonitor('advancedComponents');
  const { logError } = useExamplesStore();

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    phone: '',
    address: '',
  });

  const [formErrors, setFormErrors] = useState<Record<string, string[]>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [hasError, setHasError] = useState(false);

  // Button states
  const [buttonStates, setButtonStates] = useState({
    primary: { loading: false, success: false, error: false },
    secondary: { loading: false, success: false, error: false },
    gradient: { loading: false, success: false, error: false },
  });

  // Performance monitoring effect
  React.useEffect(() => {
    const cleanup = measureRenderTime('AdvancedComponentsExample');
    measureMemoryUsage();
    
    return cleanup;
  }, [measureRenderTime, measureMemoryUsage]);

  // Update hook status
  React.useEffect(() => {
    try {
      updateHookStatus({
        isActive: true,
        lastUsed: Date.now(),
        usageCount: 1,
      });
    } catch (error) {
      console.error('Failed to update hook status:', error);
      setHasError(true);
    }
  }, [updateHookStatus]);

  // Error handling effect
  React.useEffect(() => {
    if (hasError) {
      logError({
        message: 'AdvancedComponentsExample encountered an error',
        component: 'AdvancedComponentsExample',
        severity: 'medium',
      });
    }
  }, [hasError, logError]);

  // Memoized form validation
  const isFormValid = useMemo(() => {
    return Object.keys(formErrors).length === 0 && 
           Object.values(formData).every(value => value.trim() !== '');
  }, [formErrors, formData]);

  // Memoized form progress
  const formProgress = useMemo(() => {
    const totalFields = Object.keys(formData).length;
    const completedFields = Object.values(formData).filter(value => value.trim() !== '').length;
    return Math.round((completedFields / totalFields) * 100);
  }, [formData]);

  // Enhanced input change handler
  const handleInputChange = useCallback((field: string, value: string, isValid: boolean, errors: string[]) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setFormErrors(prev => ({ ...prev, [field]: errors }));
  }, []);

  // Form submission handler
  const handleSubmit = useCallback(async () => {
    if (!isFormValid) {
      toast.error('Please fill in all required fields correctly');
      return;
    }

    setIsSubmitting(true);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      toast.success('Form submitted successfully!');
      setFormData({ name: '', email: '', password: '', phone: '', address: '' });
      setFormErrors({});
    } catch (error) {
      toast.error('Failed to submit form');
      setHasError(true);
    } finally {
      setIsSubmitting(false);
    }
  }, [isFormValid]);

  // Button action handlers
  const handleButtonAction = useCallback(async (buttonType: keyof typeof buttonStates, action: string) => {
    setButtonStates(prev => ({
      ...prev,
      [buttonType]: { loading: true, success: false, error: false }
    }));

    try {
      // Simulate different actions
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      if (action === 'error' && Math.random() > 0.7) {
        throw new Error('Simulated error');
      }

      setButtonStates(prev => ({
        ...prev,
        [buttonType]: { loading: false, success: true, error: false }
      }));

      toast.success(`${action} completed successfully!`);
      
      // Reset success state after 2 seconds
      setTimeout(() => {
        setButtonStates(prev => ({
          ...prev,
          [buttonType]: { loading: false, success: false, error: false }
        }));
      }, 2000);

    } catch (error) {
      setButtonStates(prev => ({
        ...prev,
        [buttonType]: { loading: false, success: false, error: true }
      }));
      
      toast.error(`Failed to ${action}`);
      setHasError(true);
    }
  }, []);

  return (
    <div className="space-y-6">
      {/* Error Display */}
      {hasError && (
        <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg">
          <div className="h-5 w-5 text-red-600">⚠️</div>
          <span className="text-sm text-red-800">
            An error occurred. Check the console for details.
          </span>
        </div>
      )}

      {/* Performance Info */}
      <div className="flex items-center gap-2 p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <div className="h-5 w-5 text-blue-600">ℹ️</div>
        <span className="text-sm text-blue-800">
          This component is being monitored for performance. Check the status monitor above for metrics.
        </span>
      </div>

      {/* Form Progress */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="h-5 w-5" />
            Advanced Form Example
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Progress Bar */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span>Form Progress</span>
              <span className="font-mono">{formProgress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${formProgress}%` }}
              />
            </div>
          </div>

          {/* Form Fields */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <AdvancedInput
              label="Full Name"
              placeholder="Enter your full name"
              leftIcon={<User className="h-4 w-4" />}
              value={formData.name}
              onChange={(value, isValid, errors) => handleInputChange('name', value, isValid, errors)}
              required
              showClearButton
              variant="outline"
              size="lg"
              rounded="full"
              shadow="lg"
            />

            <AdvancedInput
              label="Email Address"
              type="email"
              placeholder="Enter your email"
              leftIcon={<Mail className="h-4 w-4" />}
              value={formData.email}
              onChange={(value, isValid, errors) => handleInputChange('email', value, isValid, errors)}
              validationRules={emailValidation}
              required
              showCharacterCount
              maxLength={50}
              variant="filled"
              size="lg"
              shadow="md"
            />

            <AdvancedInput
              label="Password"
              type="password"
              placeholder="Enter your password"
              leftIcon={<Lock className="h-4 w-4" />}
              value={formData.password}
              onChange={(value, isValid, errors) => handleInputChange('password', value, isValid, errors)}
              validationRules={passwordValidation}
              required
              showPasswordToggle
              showCharacterCount
              minLength={8}
              maxLength={128}
              variant="minimal"
              size="lg"
              animation="pulse"
            />

            <AdvancedInput
              label="Phone Number"
              type="tel"
              placeholder="Enter your phone number"
              leftIcon={<Phone className="h-4 w-4" />}
              value={formData.phone}
              onChange={(value, isValid, errors) => handleInputChange('phone', value, isValid, errors)}
              validationRules={phoneValidation}
              required
              showClearButton
              variant="outline"
              size="lg"
              rounded="full"
              shadow="sm"
            />

            <AdvancedInput
              label="Address"
              placeholder="Enter your address"
              leftIcon={<MapPin className="h-4 w-4" />}
              value={formData.address}
              onChange={(value, isValid, errors) => handleInputChange('address', value, isValid, errors)}
              required
              showClearButton
              variant="default"
              size="lg"
              shadow="md"
            />
          </div>

          {/* Submit Button */}
          <AdvancedButton
            onClick={handleSubmit}
            loading={isSubmitting}
            disabled={!isFormValid}
            size="lg"
            variant="gradient"
            gradient="blue"
            rounded="full"
            shadow="xl"
            animation="pulse"
            tooltip={!isFormValid ? 'Please fill in all required fields correctly' : 'Submit the form'}
            className="w-full"
          >
            {isSubmitting ? 'Submitting...' : 'Submit Form'}
          </AdvancedButton>
        </CardContent>
      </Card>

      <Separator />

      {/* Advanced Buttons Showcase */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5" />
            Advanced Buttons Showcase
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Primary Actions */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold">Primary Actions</h3>
            <div className="flex flex-wrap gap-3">
              <AdvancedButton
                onClick={() => handleButtonAction('primary', 'save')}
                loading={buttonStates.primary.loading}
                success={buttonStates.primary.success}
                error={buttonStates.primary.error}
                icon={<Star className="h-4 w-4" />}
                badge="New"
                size="lg"
                variant="gradient"
                gradient="green"
                rounded="full"
                shadow="lg"
                animation="bounce"
                tooltip="Save your changes with enhanced styling"
              >
                Save Changes
              </AdvancedButton>

              <AdvancedButton
                onClick={() => handleButtonAction('secondary', 'download')}
                loading={buttonStates.secondary.loading}
                success={buttonStates.secondary.success}
                error={buttonStates.secondary.error}
                icon={<Download className="h-4 w-4" />}
                iconPosition="right"
                size="lg"
                variant="outline"
                rounded="full"
                shadow="md"
                tooltip="Download the latest version"
              >
                Download
              </AdvancedButton>

              <AdvancedButton
                onClick={() => handleButtonAction('gradient', 'upload')}
                loading={buttonStates.gradient.loading}
                success={buttonStates.gradient.success}
                error={buttonStates.gradient.error}
                icon={<Upload className="h-4 w-4" />}
                size="lg"
                variant="gradient"
                gradient="purple"
                rounded="full"
                shadow="xl"
                animation="pulse"
                tooltip="Upload your files with style"
              >
                Upload Files
              </AdvancedButton>
            </div>
          </div>

          {/* Media Controls */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold">Media Controls</h3>
            <div className="flex flex-wrap gap-3">
              <AdvancedButton
                onClick={() => toast.success('Play action triggered!')}
                icon={<Play className="h-4 w-4" />}
                size="lg"
                variant="gradient"
                gradient="blue"
                rounded="full"
                shadow="lg"
                animation="ping"
                tooltip="Start playback"
              >
                Play
              </AdvancedButton>

              <AdvancedButton
                onClick={() => toast.info('Pause action triggered!')}
                icon={<Pause className="h-4 w-4" />}
                size="lg"
                variant="outline"
                rounded="full"
                shadow="md"
                tooltip="Pause playback"
              >
                Pause
              </AdvancedButton>

              <AdvancedButton
                onClick={() => toast.warning('Stop action triggered!')}
                icon={<Stop className="h-4 w-4" />}
                size="lg"
                variant="destructive"
                rounded="full"
                shadow="lg"
                animation="shake"
                tooltip="Stop playback"
              >
                Stop
              </AdvancedButton>
            </div>
          </div>

          {/* Interactive Buttons */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold">Interactive Features</h3>
            <div className="flex flex-wrap gap-3">
              <AdvancedButton
                onClick={() => toast.success('Settings opened!')}
                icon={<Settings className="h-4 w-4" />}
                size="lg"
                variant="ghost"
                rounded="full"
                shadow="sm"
                animation="bounce"
                tooltip="Open settings panel"
              >
                Settings
              </AdvancedButton>

              <AdvancedButton
                onClick={() => toast.success('Favorite added!')}
                icon={<Heart className="h-4 w-4" />}
                size="lg"
                variant="gradient"
                gradient="red"
                rounded="full"
                shadow="lg"
                animation="pulse"
                tooltip="Add to favorites"
              >
                Add to Favorites
              </AdvancedButton>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Component Features */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Star className="h-5 w-5" />
            Component Features
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="h-12 w-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <Zap className="h-6 w-6 text-blue-600" />
              </div>
              <h4 className="font-semibold text-blue-900 mb-2">Performance Monitoring</h4>
              <p className="text-sm text-blue-700">
                Real-time performance tracking with render time and memory usage monitoring
              </p>
            </div>

            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="h-12 w-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <CheckCircle className="h-6 w-6 text-green-600" />
              </div>
              <h4 className="font-semibold text-green-900 mb-2">Real-time Validation</h4>
              <p className="text-sm text-green-700">
                Instant form validation with custom rules and visual feedback
              </p>
            </div>

            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="h-12 w-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <Heart className="h-6 w-6 text-purple-600" />
              </div>
              <h4 className="font-semibold text-purple-900 mb-2">Enhanced UX</h4>
              <p className="text-sm text-purple-700">
                Rich interactions with tooltips, animations, and status indicators
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Usage Tips */}
      <div className="text-sm text-muted-foreground space-y-2">
        <p>💡 <strong>Tip:</strong> Try different button variants, sizes, and animations to see the enhanced functionality.</p>
        <p>🔧 <strong>Feature:</strong> All inputs include real-time validation with custom rules and visual feedback.</p>
        <p>📊 <strong>Monitor:</strong> Check the performance metrics in the status monitor above.</p>
        <p>🎨 <strong>Customize:</strong> Use the gradient variants and animation options for engaging user interfaces.</p>
      </div>
    </div>
  );
}





