import React, { Component, ErrorInfo, ReactNode } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

// ============================================================================
// TYPES
// ============================================================================
interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  shouldResetOnError?: boolean;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

// ============================================================================
// STATIC CONTENT
// ============================================================================
const DEFAULT_ERROR_MESSAGE = 'Something went wrong. Please try again.';
const RESET_BUTTON_TEXT = 'Try Again';
const REPORT_BUTTON_TEXT = 'Report Issue';

// ============================================================================
// HELPERS
// ============================================================================
const logErrorToService = (error: Error, errorInfo: ErrorInfo): void => {
  // In production, this would send to Sentry, Crashlytics, etc.
  console.error('Error Boundary caught an error:', error, errorInfo);
  
  // Simulate error reporting service
  try {
    // This would be replaced with actual error reporting service
    const errorReport = {
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      timestamp: new Date().toISOString(),
      userAgent: 'React Native App',
    };
    
    console.log('Error report prepared:', errorReport);
  } catch (reportingError) {
    console.error('Failed to prepare error report:', reportingError);
  }
};

const getErrorMessage = (error: Error): string => {
  if (error.message.includes('Network')) {
    return 'Network connection issue. Please check your internet connection.';
  }
  
  if (error.message.includes('Timeout')) {
    return 'Request timed out. Please try again.';
  }
  
  if (error.message.includes('Unauthorized')) {
    return 'Authentication required. Please log in again.';
  }
  
  return DEFAULT_ERROR_MESSAGE;
};

// ============================================================================
// SUBCOMPONENTS
// ============================================================================
const DefaultErrorFallback: React.FC<{
  error: Error;
  errorInfo: ErrorInfo;
  onReset: () => void;
  onReport: () => void;
}> = ({ error, errorInfo, onReset, onReport }) => {
  const errorMessage = getErrorMessage(error);
  
  return (
    <View style={styles.errorContainer}>
      <View style={styles.errorContent}>
        <Text style={styles.errorTitle}>Oops!</Text>
        <Text style={styles.errorMessage}>{errorMessage}</Text>
        
        <View style={styles.buttonContainer}>
          <TouchableOpacity style={styles.resetButton} onPress={onReset}>
            <Text style={styles.resetButtonText}>{RESET_BUTTON_TEXT}</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.reportButton} onPress={onReport}>
            <Text style={styles.reportButtonText}>{REPORT_BUTTON_TEXT}</Text>
          </TouchableOpacity>
        </View>
        
        {__DEV__ && (
          <View style={styles.debugContainer}>
            <Text style={styles.debugTitle}>Debug Information:</Text>
            <Text style={styles.debugText}>{error.message}</Text>
            <Text style={styles.debugText}>{errorInfo.componentStack}</Text>
          </View>
        )}
      </View>
    </View>
  );
};

// ============================================================================
// MAIN EXPORTED COMPONENT
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

    // Log error to service
    logErrorToService(error, errorInfo);

    // Call custom error handler if provided
    this.props.onError?.(error, errorInfo);
  }

  handleReset = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  handleReport = (): void => {
    const { error, errorInfo } = this.state;
    
    if (error && errorInfo) {
      logErrorToService(error, errorInfo);
    }
  };

  render(): ReactNode {
    const { hasError, error, errorInfo } = this.state;
    const { children, fallback } = this.props;

    if (!hasError) {
      return children;
    }

    if (fallback) {
      return fallback;
    }

    if (!error || !errorInfo) {
      return (
        <View style={styles.errorContainer}>
          <Text style={styles.errorMessage}>{DEFAULT_ERROR_MESSAGE}</Text>
        </View>
      );
    }

    return (
      <DefaultErrorFallback
        error={error}
        errorInfo={errorInfo}
        onReset={this.handleReset}
        onReport={this.handleReport}
      />
    );
  }
}

// ============================================================================
// STYLES
// ============================================================================
const styles = StyleSheet.create({
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f8f9fa',
    padding: 20,
  },
  errorContent: {
    maxWidth: 400,
    alignItems: 'center',
  },
  errorTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#dc3545',
    marginBottom: 16,
  },
  errorMessage: {
    fontSize: 16,
    color: '#6c757d',
    textAlign: 'center',
    marginBottom: 24,
    lineHeight: 24,
  },
  buttonContainer: {
    flexDirection: 'row',
    gap: 12,
  },
  resetButton: {
    backgroundColor: '#007bff',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  resetButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  reportButton: {
    backgroundColor: '#6c757d',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  reportButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  debugContainer: {
    marginTop: 24,
    padding: 16,
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#dee2e6',
  },
  debugTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#495057',
    marginBottom: 8,
  },
  debugText: {
    fontSize: 12,
    color: '#6c757d',
    fontFamily: 'monospace',
    marginBottom: 4,
  },
});

// ============================================================================
// SPECIALIZED EXPORTS
// ============================================================================
export const withErrorBoundary = <P extends object>(
  Component: React.ComponentType<P>,
  errorBoundaryProps?: Omit<ErrorBoundaryProps, 'children'>
) => {
  const WrappedComponent = (props: P) => (
    <ErrorBoundary {...errorBoundaryProps}>
      <Component {...props} />
    </ErrorBoundary>
  );
  
  WrappedComponent.displayName = `withErrorBoundary(${Component.displayName || Component.name})`;
  
  return WrappedComponent;
};

export const createErrorBoundary = (fallback?: ReactNode) => {
  return ({ children }: { children: ReactNode }) => (
    <ErrorBoundary fallback={fallback}>
      {children}
    </ErrorBoundary>
  );
}; 