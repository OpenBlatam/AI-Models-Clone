'use client';

import React, { useState } from 'react';
import { 
  AdvancedButton, 
  PrimaryButton, 
  SecondaryButton, 
  OutlineButton, 
  GhostButton, 
  DestructiveButton, 
  SuccessButton, 
  WarningButton 
} from '@/components/ui/advanced-button';
import { 
  AdvancedInput, 
  SearchInput, 
  PasswordInput, 
  EmailInput, 
  NumberInput 
} from '@/components/ui/advanced-input';
import { useToast } from '@/components/ui/toast-notifications';
import { 
  Search, 
  User, 
  Mail, 
  Lock, 
  Settings, 
  Download, 
  Upload, 
  Trash2,
  Plus,
  Edit,
  Eye,
  Heart
} from 'lucide-react';

export function ComponentsShowcase() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    age: '',
    search: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const toast = useToast();

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    toast.success('Form submitted successfully!', 'Your information has been saved.');
    setIsLoading(false);
  };

  const showToast = (type: 'success' | 'error' | 'warning' | 'info') => {
    const messages = {
      success: { title: 'Success!', message: 'Operation completed successfully.' },
      error: { title: 'Error!', message: 'Something went wrong. Please try again.' },
      warning: { title: 'Warning!', message: 'Please review your input before proceeding.' },
      info: { title: 'Info', message: 'Here is some helpful information.' },
    };
    
    toast[type](messages[type].title, messages[type].message);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Advanced UI Components Showcase
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Explore our comprehensive collection of optimized, accessible, and performant UI components
            built with modern React patterns and TypeScript.
          </p>
        </div>

        {/* Buttons Section */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold text-gray-900 mb-8 text-center">Advanced Buttons</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Button Variants */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Button Variants</h3>
              <div className="space-y-3">
                <PrimaryButton fullWidth>Primary Button</PrimaryButton>
                <SecondaryButton fullWidth>Secondary Button</SecondaryButton>
                <OutlineButton fullWidth>Outline Button</OutlineButton>
                <GhostButton fullWidth>Ghost Button</GhostButton>
                <DestructiveButton fullWidth>Destructive Button</DestructiveButton>
                <SuccessButton fullWidth>Success Button</SuccessButton>
                <WarningButton fullWidth>Warning Button</WarningButton>
              </div>
            </div>

            {/* Button Sizes */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Button Sizes</h3>
              <div className="space-y-3">
                <PrimaryButton size="xs" fullWidth>Extra Small</PrimaryButton>
                <PrimaryButton size="sm" fullWidth>Small</PrimaryButton>
                <PrimaryButton size="md" fullWidth>Medium</PrimaryButton>
                <PrimaryButton size="lg" fullWidth>Large</PrimaryButton>
                <PrimaryButton size="xl" fullWidth>Extra Large</PrimaryButton>
              </div>
            </div>

            {/* Button States */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Button States</h3>
              <div className="space-y-3">
                <PrimaryButton loading fullWidth>Loading Button</PrimaryButton>
                <PrimaryButton disabled fullWidth>Disabled Button</PrimaryButton>
                <PrimaryButton 
                  leftIcon={<Plus className="w-4 h-4" />} 
                  fullWidth
                >
                  With Left Icon
                </PrimaryButton>
                <PrimaryButton 
                  rightIcon={<ArrowRight className="w-4 h-4" />} 
                  fullWidth
                >
                  With Right Icon
                </PrimaryButton>
              </div>
            </div>
          </div>
        </section>

        {/* Inputs Section */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold text-gray-900 mb-8 text-center">Advanced Inputs</h2>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Form Inputs */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Form Inputs</h3>
              <form onSubmit={handleSubmit} className="space-y-4">
                <AdvancedInput
                  label="Full Name"
                  placeholder="Enter your full name"
                  value={formData.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  leftIcon={<User className="w-4 h-4" />}
                  required
                />
                
                <EmailInput
                  label="Email Address"
                  placeholder="Enter your email"
                  value={formData.email}
                  onChange={(e) => handleInputChange('email', e.target.value)}
                  leftIcon={<Mail className="w-4 h-4" />}
                  required
                />
                
                <PasswordInput
                  label="Password"
                  placeholder="Enter your password"
                  value={formData.password}
                  onChange={(e) => handleInputChange('password', e.target.value)}
                  leftIcon={<Lock className="w-4 h-4" />}
                  required
                />
                
                <NumberInput
                  label="Age"
                  placeholder="Enter your age"
                  value={formData.age}
                  onChange={(e) => handleInputChange('age', e.target.value)}
                  min={18}
                  max={100}
                />
                
                <PrimaryButton 
                  type="submit" 
                  loading={isLoading}
                  fullWidth
                >
                  {isLoading ? 'Submitting...' : 'Submit Form'}
                </PrimaryButton>
              </form>
            </div>

            {/* Specialized Inputs */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Specialized Inputs</h3>
              <div className="space-y-4">
                <SearchInput
                  label="Search"
                  placeholder="Search for anything..."
                  value={formData.search}
                  onChange={(e) => handleInputChange('search', e.target.value)}
                  clearable
                />
                
                <AdvancedInput
                  label="With Success State"
                  placeholder="This input shows success"
                  value="Valid input"
                  success="Input is valid!"
                  leftIcon={<CheckCircle className="w-4 h-4" />}
                />
                
                <AdvancedInput
                  label="With Error State"
                  placeholder="This input shows error"
                  value="Invalid input"
                  error="Please fix this error"
                  leftIcon={<AlertCircle className="w-4 h-4" />}
                />
                
                <AdvancedInput
                  label="Loading State"
                  placeholder="This input is loading"
                  loading
                  leftIcon={<Settings className="w-4 h-4" />}
                />
              </div>
            </div>
          </div>
        </section>

        {/* Interactive Examples */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold text-gray-900 mb-8 text-center">Interactive Examples</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Toast Demonstrations */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Toast Notifications</h3>
              <div className="space-y-3">
                <PrimaryButton 
                  size="sm" 
                  fullWidth
                  onClick={() => showToast('success')}
                >
                  Success Toast
                </PrimaryButton>
                <SecondaryButton 
                  size="sm" 
                  fullWidth
                  onClick={() => showToast('error')}
                >
                  Error Toast
                </SecondaryButton>
                <WarningButton 
                  size="sm" 
                  fullWidth
                  onClick={() => showToast('warning')}
                >
                  Warning Toast
                </WarningButton>
                <GhostButton 
                  size="sm" 
                  fullWidth
                  onClick={() => showToast('info')}
                >
                  Info Toast
                </GhostButton>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Action Buttons</h3>
              <div className="space-y-3">
                <PrimaryButton 
                  size="sm" 
                  fullWidth
                  leftIcon={<Download className="w-4 h-4" />}
                >
                  Download
                </PrimaryButton>
                <SecondaryButton 
                  size="sm" 
                  fullWidth
                  leftIcon={<Upload className="w-4 h-4" />}
                >
                  Upload
                </SecondaryButton>
                <DestructiveButton 
                  size="sm" 
                  fullWidth
                  leftIcon={<Trash2 className="w-4 h-4" />}
                >
                  Delete
                </DestructiveButton>
              </div>
            </div>

            {/* Icon Buttons */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Icon Buttons</h3>
              <div className="space-y-3">
                <PrimaryButton size="sm" rounded="full">
                  <Plus className="w-4 h-4" />
                </PrimaryButton>
                <SecondaryButton size="sm" rounded="full">
                  <Edit className="w-4 h-4" />
                </SecondaryButton>
                <GhostButton size="sm" rounded="full">
                  <Eye className="w-4 h-4" />
                </GhostButton>
                <SuccessButton size="sm" rounded="full">
                  <Heart className="w-4 h-4" />
                </SuccessButton>
              </div>
            </div>

            {/* Button Animations */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Animations</h3>
              <div className="space-y-3">
                <PrimaryButton 
                  size="sm" 
                  fullWidth
                  animation="pulse"
                >
                  Pulse Animation
                </PrimaryButton>
                <SecondaryButton 
                  size="sm" 
                  fullWidth
                  animation="bounce"
                >
                  Bounce Animation
                </SecondaryButton>
                <OutlineButton 
                  size="sm" 
                  fullWidth
                  animation="spin"
                >
                  Spin Animation
                </OutlineButton>
              </div>
            </div>
          </div>
        </section>

        {/* Performance Features */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold text-gray-900 mb-8 text-center">Performance Features</h2>
          
          <div className="bg-white rounded-lg shadow-md p-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
              <div>
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Zap className="w-8 h-8 text-blue-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Memoized Components</h3>
                <p className="text-gray-600">
                  All components use React.memo and useMemo for optimal performance
                </p>
              </div>
              
              <div>
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Shield className="w-8 h-8 text-green-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Type Safe</h3>
                <p className="text-gray-600">
                  Built with TypeScript for better developer experience and fewer runtime errors
                </p>
              </div>
              
              <div>
                <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Accessibility className="w-8 h-8 text-purple-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Accessible</h3>
                <p className="text-gray-600">
                  Full ARIA support and keyboard navigation for better accessibility
                </p>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

// Missing icon components
const ArrowRight = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
  </svg>
);

const CheckCircle = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const AlertCircle = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const Zap = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
  </svg>
);

const Shield = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
  </svg>
);

const Accessibility = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
  </svg>
);
