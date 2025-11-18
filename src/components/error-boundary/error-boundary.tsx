import React, { Component, ErrorInfo, ReactNode } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useColorScheme } from 'react-native';
import { z } from 'zod';

// ============================================================================
// TYPES
// ============================================================================

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface ErrorDetails {
  message: string;
  stack?: string;
  componentStack?: string;
  timestamp: string;
  userAgent?: string;
  platform: string;
}

// ============================================================================
// VALIDATION SCHEMAS
// ============================================================================

const ErrorDetailsSchema = z.object({
  message: z.string(),
  stack: z.string().optional(),
  componentStack: z.string().optional(),
  timestamp: z.string(),
  userAgent: z.string().optional(),
  platform: z.string(),
});

// ============================================================================
// ERROR BOUNDARY COMPONENT
// ============================================================================

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    this.setState({
      error,
      errorInfo,
    });

    // Log error details
    this.logError(error, errorInfo);

    // Call custom error handler if provided
    this.props.onError?.(error, errorInfo);
  }

  private logError = (error: Error, errorInfo: ErrorInfo): void => {
    const errorDetails: ErrorDetails = {
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      timestamp: new Date().toISOString(),
      platform: 'react-native',
    };

    // Validate error details with Zod
    try {
      const validatedError = ErrorDetailsSchema.parse(errorDetails);
      console.error('Error Boundary caught an error:', validatedError);
      
      // Here you would typically send to your error reporting service
      // Example: Sentry.captureException(error, { extra: validatedError });
    } catch (validationError) {
      console.error('Error validation failed:', validationError);
    }
  };

  private handleRetry = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  private handleReportError = (): void => {
    const { error, errorInfo } = this.state;
    if (error && errorInfo) {
      // Here you would implement error reporting logic
      console.log('Reporting error to service...');
    }
  };

  render(): ReactNode {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return <ErrorFallback 
        error={this.state.error} 
        errorInfo={this.state.errorInfo}
        onRetry={this.handleRetry}
        onReportError={this.handleReportError}
      />;
    }

    return this.props.children;
  }
}

// ============================================================================
// ERROR FALLBACK COMPONENT
// ============================================================================

interface ErrorFallbackProps {
  error: Error | null;
  errorInfo: ErrorInfo | null;
  onRetry: () => void;
  onReportError: () => void;
}

function ErrorFallback({ error, errorInfo, onRetry, onReportError }: ErrorFallbackProps): JSX.Element {
  const colorScheme = useColorScheme();
  const isDark = colorScheme === 'dark';
  const styles = createStyles(isDark);

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.header}>
          <Ionicons 
            name="warning-outline" 
            size={64} 
            color={isDark ? '#FF6B6B' : '#FF3B30'} 
          />
          <Text style={styles.title}>Oops! Something went wrong</Text>
          <Text style={styles.subtitle}>
            We're sorry, but something unexpected happened. Please try again.
          </Text>
        </View>

        <View style={styles.actions}>
          <TouchableOpacity style={styles.retryButton} onPress={onRetry}>
            <Ionicons name="refresh" size={20} color="#FFFFFF" />
            <Text style={styles.retryButtonText}>Try Again</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.reportButton} onPress={onReportError}>
            <Ionicons name="bug-outline" size={20} color={isDark ? '#FFFFFF' : '#000000'} />
            <Text style={styles.reportButtonText}>Report Issue</Text>
          </TouchableOpacity>
        </View>

        {__DEV__ && error && (
          <View style={styles.errorDetails}>
            <Text style={styles.errorDetailsTitle}>Error Details (Development Only)</Text>
            <Text style={styles.errorMessage}>{error.message}</Text>
            {error.stack && (
              <Text style={styles.errorStack}>{error.stack}</Text>
            )}
            {errorInfo?.componentStack && (
              <Text style={styles.componentStack}>{errorInfo.componentStack}</Text>
            )}
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

// ============================================================================
// STYLES
// ============================================================================

function createStyles(isDark: boolean) {
  return StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: isDark ? '#000000' : '#FFFFFF',
    },
    scrollContent: {
      flexGrow: 1,
      justifyContent: 'center',
      alignItems: 'center',
      padding: 20,
    },
    header: {
      alignItems: 'center',
      marginBottom: 40,
    },
    title: {
      fontSize: 24,
      fontWeight: 'bold',
      color: isDark ? '#FFFFFF' : '#000000',
      textAlign: 'center',
      marginTop: 16,
      marginBottom: 8,
    },
    subtitle: {
      fontSize: 16,
      color: isDark ? '#8E8E93' : '#6C6C70',
      textAlign: 'center',
      lineHeight: 24,
    },
    actions: {
      width: '100%',
      maxWidth: 300,
    },
    retryButton: {
      backgroundColor: '#007AFF',
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'center',
      paddingVertical: 16,
      paddingHorizontal: 24,
      borderRadius: 12,
      marginBottom: 12,
    },
    retryButtonText: {
      color: '#FFFFFF',
      fontSize: 16,
      fontWeight: '600',
      marginLeft: 8,
    },
    reportButton: {
      backgroundColor: isDark ? '#2C2C2E' : '#F2F2F7',
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'center',
      paddingVertical: 16,
      paddingHorizontal: 24,
      borderRadius: 12,
      borderWidth: 1,
      borderColor: isDark ? '#3A3A3C' : '#E5E5EA',
    },
    reportButtonText: {
      color: isDark ? '#FFFFFF' : '#000000',
      fontSize: 16,
      fontWeight: '600',
      marginLeft: 8,
    },
    errorDetails: {
      width: '100%',
      marginTop: 40,
      padding: 16,
      backgroundColor: isDark ? '#1C1C1E' : '#F8F9FA',
      borderRadius: 12,
      borderWidth: 1,
      borderColor: isDark ? '#3A3A3C' : '#E5E5EA',
    },
    errorDetailsTitle: {
      fontSize: 16,
      fontWeight: '600',
      color: isDark ? '#FFFFFF' : '#000000',
      marginBottom: 12,
    },
    errorMessage: {
      fontSize: 14,
      color: '#FF3B30',
      marginBottom: 8,
      fontFamily: 'monospace',
    },
    errorStack: {
      fontSize: 12,
      color: isDark ? '#8E8E93' : '#6C6C70',
      marginBottom: 8,
      fontFamily: 'monospace',
    },
    componentStack: {
      fontSize: 12,
      color: isDark ? '#8E8E93' : '#6C6C70',
      fontFamily: 'monospace',
    },
  });
}

// ============================================================================
// HOOK FOR ERROR HANDLING
// ============================================================================

export function useErrorHandler() {
  const handleError = (error: Error, context?: string): void => {
    const errorDetails: ErrorDetails = {
      message: error.message,
      stack: error.stack,
      timestamp: new Date().toISOString(),
      platform: 'react-native',
    };

    try {
      const validatedError = ErrorDetailsSchema.parse(errorDetails);
      console.error(`Error in ${context || 'unknown context'}:`, validatedError);
      
      // Here you would typically send to your error reporting service
      // Example: Sentry.captureException(error, { extra: validatedError });
    } catch (validationError) {
      console.error('Error validation failed:', validationError);
    }
  };

  return { handleError };
}
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useColorScheme } from 'react-native';
import { z } from 'zod';

// ============================================================================
// TYPES
// ============================================================================

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface ErrorDetails {
  message: string;
  stack?: string;
  componentStack?: string;
  timestamp: string;
  userAgent?: string;
  platform: string;
}

// ============================================================================
// VALIDATION SCHEMAS
// ============================================================================

const ErrorDetailsSchema = z.object({
  message: z.string(),
  stack: z.string().optional(),
  componentStack: z.string().optional(),
  timestamp: z.string(),
  userAgent: z.string().optional(),
  platform: z.string(),
});

// ============================================================================
// ERROR BOUNDARY COMPONENT
// ============================================================================

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    this.setState({
      error,
      errorInfo,
    });

    // Log error details
    this.logError(error, errorInfo);

    // Call custom error handler if provided
    this.props.onError?.(error, errorInfo);
  }

  private logError = (error: Error, errorInfo: ErrorInfo): void => {
    const errorDetails: ErrorDetails = {
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      timestamp: new Date().toISOString(),
      platform: 'react-native',
    };

    // Validate error details with Zod
    try {
      const validatedError = ErrorDetailsSchema.parse(errorDetails);
      console.error('Error Boundary caught an error:', validatedError);
      
      // Here you would typically send to your error reporting service
      // Example: Sentry.captureException(error, { extra: validatedError });
    } catch (validationError) {
      console.error('Error validation failed:', validationError);
    }
  };

  private handleRetry = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  private handleReportError = (): void => {
    const { error, errorInfo } = this.state;
    if (error && errorInfo) {
      // Here you would implement error reporting logic
      console.log('Reporting error to service...');
    }
  };

  render(): ReactNode {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return <ErrorFallback 
        error={this.state.error} 
        errorInfo={this.state.errorInfo}
        onRetry={this.handleRetry}
        onReportError={this.handleReportError}
      />;
    }

    return this.props.children;
  }
}

// ============================================================================
// ERROR FALLBACK COMPONENT
// ============================================================================

interface ErrorFallbackProps {
  error: Error | null;
  errorInfo: ErrorInfo | null;
  onRetry: () => void;
  onReportError: () => void;
}

function ErrorFallback({ error, errorInfo, onRetry, onReportError }: ErrorFallbackProps): JSX.Element {
  const colorScheme = useColorScheme();
  const isDark = colorScheme === 'dark';
  const styles = createStyles(isDark);

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.header}>
          <Ionicons 
            name="warning-outline" 
            size={64} 
            color={isDark ? '#FF6B6B' : '#FF3B30'} 
          />
          <Text style={styles.title}>Oops! Something went wrong</Text>
          <Text style={styles.subtitle}>
            We're sorry, but something unexpected happened. Please try again.
          </Text>
        </View>

        <View style={styles.actions}>
          <TouchableOpacity style={styles.retryButton} onPress={onRetry}>
            <Ionicons name="refresh" size={20} color="#FFFFFF" />
            <Text style={styles.retryButtonText}>Try Again</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.reportButton} onPress={onReportError}>
            <Ionicons name="bug-outline" size={20} color={isDark ? '#FFFFFF' : '#000000'} />
            <Text style={styles.reportButtonText}>Report Issue</Text>
          </TouchableOpacity>
        </View>

        {__DEV__ && error && (
          <View style={styles.errorDetails}>
            <Text style={styles.errorDetailsTitle}>Error Details (Development Only)</Text>
            <Text style={styles.errorMessage}>{error.message}</Text>
            {error.stack && (
              <Text style={styles.errorStack}>{error.stack}</Text>
            )}
            {errorInfo?.componentStack && (
              <Text style={styles.componentStack}>{errorInfo.componentStack}</Text>
            )}
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

// ============================================================================
// STYLES
// ============================================================================

function createStyles(isDark: boolean) {
  return StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: isDark ? '#000000' : '#FFFFFF',
    },
    scrollContent: {
      flexGrow: 1,
      justifyContent: 'center',
      alignItems: 'center',
      padding: 20,
    },
    header: {
      alignItems: 'center',
      marginBottom: 40,
    },
    title: {
      fontSize: 24,
      fontWeight: 'bold',
      color: isDark ? '#FFFFFF' : '#000000',
      textAlign: 'center',
      marginTop: 16,
      marginBottom: 8,
    },
    subtitle: {
      fontSize: 16,
      color: isDark ? '#8E8E93' : '#6C6C70',
      textAlign: 'center',
      lineHeight: 24,
    },
    actions: {
      width: '100%',
      maxWidth: 300,
    },
    retryButton: {
      backgroundColor: '#007AFF',
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'center',
      paddingVertical: 16,
      paddingHorizontal: 24,
      borderRadius: 12,
      marginBottom: 12,
    },
    retryButtonText: {
      color: '#FFFFFF',
      fontSize: 16,
      fontWeight: '600',
      marginLeft: 8,
    },
    reportButton: {
      backgroundColor: isDark ? '#2C2C2E' : '#F2F2F7',
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'center',
      paddingVertical: 16,
      paddingHorizontal: 24,
      borderRadius: 12,
      borderWidth: 1,
      borderColor: isDark ? '#3A3A3C' : '#E5E5EA',
    },
    reportButtonText: {
      color: isDark ? '#FFFFFF' : '#000000',
      fontSize: 16,
      fontWeight: '600',
      marginLeft: 8,
    },
    errorDetails: {
      width: '100%',
      marginTop: 40,
      padding: 16,
      backgroundColor: isDark ? '#1C1C1E' : '#F8F9FA',
      borderRadius: 12,
      borderWidth: 1,
      borderColor: isDark ? '#3A3A3C' : '#E5E5EA',
    },
    errorDetailsTitle: {
      fontSize: 16,
      fontWeight: '600',
      color: isDark ? '#FFFFFF' : '#000000',
      marginBottom: 12,
    },
    errorMessage: {
      fontSize: 14,
      color: '#FF3B30',
      marginBottom: 8,
      fontFamily: 'monospace',
    },
    errorStack: {
      fontSize: 12,
      color: isDark ? '#8E8E93' : '#6C6C70',
      marginBottom: 8,
      fontFamily: 'monospace',
    },
    componentStack: {
      fontSize: 12,
      color: isDark ? '#8E8E93' : '#6C6C70',
      fontFamily: 'monospace',
    },
  });
}

// ============================================================================
// HOOK FOR ERROR HANDLING
// ============================================================================

export function useErrorHandler() {
  const handleError = (error: Error, context?: string): void => {
    const errorDetails: ErrorDetails = {
      message: error.message,
      stack: error.stack,
      timestamp: new Date().toISOString(),
      platform: 'react-native',
    };

    try {
      const validatedError = ErrorDetailsSchema.parse(errorDetails);
      console.error(`Error in ${context || 'unknown context'}:`, validatedError);
      
      // Here you would typically send to your error reporting service
      // Example: Sentry.captureException(error, { extra: validatedError });
    } catch (validationError) {
      console.error('Error validation failed:', validationError);
    }
  };

  return { handleError };
}


