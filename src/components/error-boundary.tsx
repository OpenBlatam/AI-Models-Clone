'use client';

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { AlertTriangle, RefreshCw, Home, Bug, Info } from 'lucide-react';
import { useExamplesStore } from '@/lib/stores/examples-store';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  errorId: string;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: '',
    };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    const errorId = `error-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    this.setState({
      error,
      errorInfo,
      errorId,
    });

    // Log error to store if available
    try {
      const { logError } = useExamplesStore.getState();
      logError({
        message: error.message,
        component: errorInfo.componentStack.split('\n')[1]?.trim() || 'Unknown',
        severity: 'high',
      });
    } catch (storeError) {
      console.error('Failed to log error to store:', storeError);
    }

    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      console.group(`🚨 Error Boundary Caught: ${errorId}`);
      console.error('Error:', error);
      console.error('Error Info:', errorInfo);
      console.groupEnd();
    }

    // Call custom error handler if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: '',
    });
  };

  handleGoHome = () => {
    window.location.href = '/';
  };

  handleReportError = () => {
    const { error, errorInfo, errorId } = this.state;
    const errorReport = {
      id: errorId,
      message: error?.message || 'Unknown error',
      stack: error?.stack || 'No stack trace',
      componentStack: errorInfo?.componentStack || 'No component stack',
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href,
    };

    // In production, you would send this to your error reporting service
    if (process.env.NODE_ENV === 'production') {
      console.log('Error report:', errorReport);
      // Example: sendToErrorService(errorReport);
    } else {
      console.group('📋 Error Report');
      console.log('Error ID:', errorReport.id);
      console.log('Message:', errorReport.message);
      console.log('Stack:', errorReport.stack);
      console.log('Component Stack:', errorReport.componentStack);
      console.log('Timestamp:', errorReport.timestamp);
      console.log('URL:', errorReport.url);
      console.groupEnd();
    }
  };

  render() {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default fallback UI
      return (
        <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-red-50 to-orange-50">
          <Card className="w-full max-w-2xl border-red-200 shadow-lg">
            <CardHeader className="text-center border-b border-red-100">
              <div className="flex items-center justify-center gap-3 mb-4">
                <div className="p-3 bg-red-100 rounded-full">
                  <AlertTriangle className="h-8 w-8 text-red-600" />
                </div>
                <div>
                  <CardTitle className="text-2xl text-red-800">
                    Something went wrong
                  </CardTitle>
                  <p className="text-red-600 mt-1">
                    We encountered an unexpected error
                  </p>
                </div>
              </div>
              <Badge variant="destructive" className="text-sm">
                Error ID: {this.state.errorId}
              </Badge>
            </CardHeader>
            
            <CardContent className="pt-6 space-y-6">
              {/* Error Details */}
              <div className="space-y-3">
                <h3 className="font-medium text-gray-900 flex items-center gap-2">
                  <Bug className="h-4 w-4" />
                  Error Details
                </h3>
                <div className="bg-gray-50 p-3 rounded-lg">
                  <p className="text-sm text-gray-700 font-mono">
                    {this.state.error?.message || 'An unknown error occurred'}
                  </p>
                </div>
              </div>

              {/* Actions */}
              <div className="flex flex-col sm:flex-row gap-3">
                <Button 
                  onClick={this.handleReset}
                  className="flex-1"
                  variant="default"
                >
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Try Again
                </Button>
                <Button 
                  onClick={this.handleGoHome}
                  className="flex-1"
                  variant="outline"
                >
                  <Home className="mr-2 h-4 w-4" />
                  Go Home
                </Button>
                <Button 
                  onClick={this.handleReportError}
                  className="flex-1"
                  variant="outline"
                >
                  <Bug className="mr-2 h-4 w-4" />
                  Report Error
                </Button>
              </div>

              {/* Development Info */}
              {process.env.NODE_ENV === 'development' && this.state.error && (
                <div className="space-y-3">
                  <h3 className="font-medium text-gray-900 flex items-center gap-2">
                    <Info className="h-4 w-4" />
                    Development Information
                  </h3>
                  <div className="space-y-2">
                    <details className="bg-gray-50 p-3 rounded-lg">
                      <summary className="cursor-pointer font-medium text-gray-700">
                        Error Stack Trace
                      </summary>
                      <pre className="text-xs text-gray-600 mt-2 whitespace-pre-wrap overflow-auto max-h-32">
                        {this.state.error.stack}
                      </pre>
                    </details>
                    {this.state.errorInfo && (
                      <details className="bg-gray-50 p-3 rounded-lg">
                        <summary className="cursor-pointer font-medium text-gray-700">
                          Component Stack
                        </summary>
                        <pre className="text-xs text-gray-600 mt-2 whitespace-pre-wrap overflow-auto max-h-32">
                          {this.state.errorInfo.componentStack}
                        </pre>
                      </details>
                    )}
                  </div>
                </div>
              )}

              {/* Help Text */}
              <div className="text-center text-sm text-gray-600 border-t border-gray-100 pt-4">
                <p>
                  If this problem persists, please contact support with the error ID above.
                </p>
                <p className="mt-1">
                  We apologize for the inconvenience.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      );
    }

    return this.props.children;
  }
}

// Hook for functional components to catch errors
export const useErrorHandler = () => {
  const { logError } = useExamplesStore();
  
  const handleError = React.useCallback((error: Error, context?: string) => {
    logError({
      message: error.message,
      component: context || 'Unknown Component',
      severity: 'medium',
    });
  }, [logError]);

  return { handleError };
};

// HOC to wrap components with error boundary
export const withErrorBoundary = <P extends object>(
  Component: React.ComponentType<P>,
  fallback?: ReactNode,
  onError?: (error: Error, errorInfo: ErrorInfo) => void
) => {
  const WrappedComponent = (props: P) => (
    <ErrorBoundary fallback={fallback} onError={onError}>
      <Component {...props} />
    </ErrorBoundary>
  );

  WrappedComponent.displayName = `withErrorBoundary(${Component.displayName || Component.name})`;
  
  return WrappedComponent;
};

export default ErrorBoundary;





