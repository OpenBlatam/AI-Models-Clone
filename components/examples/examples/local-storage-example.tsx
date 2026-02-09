'use client';

import React, { useState, useCallback, useMemo, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { useLocalStorage } from '@/hooks/use-local-storage';
import { toast } from 'react-hot-toast';
import { Save, Trash2, CheckCircle, AlertTriangle, Info } from 'lucide-react';
import { z } from 'zod';
import { usePerformanceMonitor, useHookStatusMonitor } from '@/lib/stores/examples-store';
import { useExamplesStore } from '@/lib/stores/examples-store';

// Schema definition for better type safety
const userSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
  role: z.string().min(1, 'Role is required'),
});

type UserFormData = z.infer<typeof userSchema>;

// Constants for better maintainability
const STORAGE_KEYS = {
  USER: 'example-user',
  THEME: 'example-theme',
  COUNTER: 'example-counter',
} as const;

const INITIAL_USER: UserFormData = {
  name: '',
  email: '',
  role: '',
};

const SAMPLE_USER: UserFormData = {
  name: 'John Doe',
  email: 'john@example.com',
  role: 'Admin',
};

export default function LocalStorageExample() {
  // Performance monitoring
  const { measureRenderTime, measureMemoryUsage } = usePerformanceMonitor();
  const { updateLocalStorageCount } = useHookStatusMonitor();
  const { logError } = useExamplesStore();

  // Local storage hooks with proper error handling
  const [user, setUser, removeUser] = useLocalStorage<UserFormData>(STORAGE_KEYS.USER, INITIAL_USER);
  const [theme, setTheme] = useLocalStorage<'light' | 'dark'>(STORAGE_KEYS.THEME, 'light');
  const [counter, setCounter] = useLocalStorage<number>(STORAGE_KEYS.COUNTER, 0);
  
  // Local state for UI feedback
  const [showSuccess, setShowSuccess] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [hasError, setHasError] = useState(false);

  // Memoized computed values
  const hasUserData = useMemo(() => 
    user.name || user.email || user.role, [user]
  );

  const isThemeLight = useMemo(() => theme === 'light', [theme]);

  // Performance monitoring effect
  useEffect(() => {
    const cleanup = measureRenderTime('LocalStorageExample');
    measureMemoryUsage();
    
    return cleanup;
  }, [measureRenderTime, measureMemoryUsage]);

  // Update hook status when localStorage changes
  useEffect(() => {
    const totalItems = [user, theme, counter].filter(item => item !== undefined && item !== null).length;
    updateLocalStorageCount(totalItems);
  }, [user, theme, counter, updateLocalStorageCount]);

  // Error handling effect
  useEffect(() => {
    if (hasError) {
      logError({
        message: 'LocalStorageExample encountered an error',
        component: 'LocalStorageExample',
        severity: 'medium',
      });
    }
  }, [hasError, logError]);

  // Optimized handlers with useCallback
  const handleUserChange = useCallback((field: keyof UserFormData, value: string) => {
    try {
      setUser({ ...user, [field]: value });
      setShowSuccess(true);
      setHasError(false);
      setTimeout(() => setShowSuccess(false), 2000);
    } catch (error) {
      setHasError(true);
      toast.error('Failed to save user data');
      console.error('User data save error:', error);
      
      logError({
        message: `Failed to save user data: ${error instanceof Error ? error.message : 'Unknown error'}`,
        component: 'LocalStorageExample',
        severity: 'medium',
      });
    }
  }, [user, setUser, logError]);

  const resetUser = useCallback(async () => {
    try {
      setIsProcessing(true);
      removeUser();
      toast.success('User data cleared successfully!');
    } catch (error) {
      toast.error('Failed to clear user data');
      console.error('User data clear error:', error);
    } finally {
      setIsProcessing(false);
    }
  }, [removeUser]);

  const setSampleData = useCallback(async () => {
    try {
      setIsProcessing(true);
      setUser(SAMPLE_USER);
      toast.success('Sample data loaded!');
    } catch (error) {
      toast.error('Failed to load sample data');
      console.error('Sample data load error:', error);
    } finally {
      setIsProcessing(false);
    }
  }, [setUser]);

  const toggleTheme = useCallback(() => {
    try {
      setTheme(isThemeLight ? 'dark' : 'light');
    } catch (error) {
      toast.error('Failed to toggle theme');
      console.error('Theme toggle error:', error);
    }
  }, [isThemeLight, setTheme]);

  const updateCounter = useCallback((delta: number) => {
    try {
      setCounter(counter + delta);
    } catch (error) {
      toast.error('Failed to update counter');
      console.error('Counter update error:', error);
    }
  }, [counter, setCounter]);

  const resetCounter = useCallback(() => {
    try {
      setCounter(0);
    } catch (error) {
      toast.error('Failed to reset counter');
      console.error('Counter reset error:', error);
    }
  }, [setCounter]);

  // Early return for error states
  if (!user || !theme || counter === undefined) {
    return (
      <div className="text-center py-8">
        <p className="text-destructive">Failed to load local storage data</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Error Display */}
      {hasError && (
        <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg">
          <AlertTriangle className="h-5 w-5 text-red-600" />
          <span className="text-sm text-red-800">
            An error occurred while saving data. Please try again.
          </span>
        </div>
      )}

      {/* Performance Info */}
      <div className="flex items-center gap-2 p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <Info className="h-5 w-5 text-blue-600" />
        <span className="text-sm text-blue-800">
          This component is being monitored for performance. Check the status monitor above for metrics.
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* User Form Card */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">User Data</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="space-y-2">
              <label htmlFor="user-name" className="text-sm font-medium">
                Name
              </label>
              <Input
                id="user-name"
                placeholder="Enter your name"
                value={user.name}
                onChange={(e) => handleUserChange('name', e.target.value)}
                disabled={isProcessing}
                aria-describedby="name-help"
                aria-invalid={hasError}
              />
              <p id="name-help" className="text-xs text-muted-foreground">
                Enter at least 2 characters
              </p>
            </div>
            <div className="space-y-2">
              <label htmlFor="user-email" className="text-sm font-medium">
                Email
              </label>
              <Input
                id="user-email"
                type="email"
                placeholder="Enter your email"
                value={user.email}
                onChange={(e) => handleUserChange('email', e.target.value)}
                disabled={isProcessing}
                aria-describedby="email-help"
                aria-invalid={hasError}
                data-testid="user-email-input"
              />
              <p id="email-help" className="text-xs text-muted-foreground">
                Enter a valid email address
              </p>
            </div>
            <div className="space-y-2">
              <label htmlFor="user-role" className="text-sm font-medium">
                Role
              </label>
              <Input
                id="user-role"
                placeholder="Enter your role"
                value={user.role}
                onChange={(e) => handleUserChange('role', e.target.value)}
                disabled={isProcessing}
                aria-describedby="role-help"
                aria-invalid={hasError}
                data-testid="user-role-input"
              />
              <p id="role-help" className="text-xs text-muted-foreground">
                Enter your job role or title
              </p>
            </div>
            <div className="flex gap-2">
              <Button 
                size="sm" 
                onClick={setSampleData}
                disabled={isProcessing}
                className="flex-1"
                data-testid="set-sample-button"
                aria-label="Set sample user data"
              >
                <Save className="h-4 w-4 mr-2" />
                Set Sample
              </Button>
              <Button 
                size="sm" 
                variant="outline" 
                onClick={resetUser}
                disabled={isProcessing}
                data-testid="clear-user-button"
                aria-label="Clear user data"
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Clear
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Theme Toggle Card */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Theme</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="space-y-2">
              <label className="text-sm font-medium">Current Theme</label>
              <div className="flex items-center gap-2">
                <Badge variant={isThemeLight ? 'default' : 'secondary'}>
                  {theme}
                </Badge>
                <span className="text-xs text-muted-foreground">
                  {isThemeLight ? 'Light mode active' : 'Dark mode active'}
                </span>
              </div>
            </div>
            <Button 
              size="sm" 
              onClick={toggleTheme}
              disabled={isProcessing}
              className="w-full"
              data-testid="toggle-theme-button"
              aria-label={`Switch to ${isThemeLight ? 'dark' : 'light'} theme`}
            >
              Switch to {isThemeLight ? 'Dark' : 'Light'}
            </Button>
          </CardContent>
        </Card>

        {/* Counter Card */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Counter</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="text-2xl font-bold text-center">{counter}</div>
            <div className="flex gap-2">
              <Button 
                size="sm" 
                onClick={() => updateCounter(-1)}
                disabled={isProcessing}
              >
                -
              </Button>
              <Button 
                size="sm" 
                onClick={() => updateCounter(1)}
                disabled={isProcessing}
              >
                +
              </Button>
              <Button 
                size="sm" 
                variant="outline" 
                onClick={resetCounter}
                disabled={isProcessing}
              >
                Reset
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Success Feedback */}
      {showSuccess && (
        <div className="flex items-center gap-2 p-3 bg-green-50 border border-green-200 rounded-lg">
          <CheckCircle className="h-5 w-5 text-green-600" />
          <span className="text-sm text-green-800">Data saved to local storage!</span>
        </div>
      )}
      
      {/* User Tips */}
      <div className="text-sm text-muted-foreground">
        <p>💡 Try changing values and refreshing the page - they'll persist!</p>
        {hasUserData && (
          <p className="mt-2">✅ User data is currently stored in local storage</p>
        )}
      </div>
    </div>
  );
}
