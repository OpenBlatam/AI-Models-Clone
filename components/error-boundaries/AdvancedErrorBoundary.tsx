'use client';

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Button } from '@/components/ui/button';
import { AlertTriangle, RefreshCw, Home, Bug, X } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  resetKeys?: any[];
  showResetButton?: boolean;
  showHomeButton?: boolean;
  showReportButton?: boolean;
  className?: string;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  errorId: string;
  isReporting: boolean;
  showDetails: boolean;
}

export class AdvancedErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: '',
      isReporting: false,
      showDetails: false,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return {
      hasError: true,
      error,
      errorId: this.generateErrorId(),
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({
      errorInfo,
    });

    // Log error to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('Error Boundary caught an error:', error, errorInfo);
    }

    // Call custom error handler if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // Report error to external service (e.g., Sentry, LogRocket)
    this.reportError(error, errorInfo);
  }

  componentDidUpdate(prevProps: Props) {
    // Reset error state when resetKeys change
    if (this.props.resetKeys && prevProps.resetKeys !== this.props.resetKeys) {
      this.setState({
        hasError: false,
        error: null,
        errorInfo: null,
        errorId: '',
        showDetails: false,
      });
    }
  }

  private static generateErrorId(): string {
    return `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private reportError = async (error: Error, errorInfo: ErrorInfo) => {
    if (this.state.isReporting) return;

    this.setState({ isReporting: true });

    try {
      // Example error reporting to external service
      const errorReport = {
        id: this.state.errorId,
        message: error.message,
        stack: error.stack,
        componentStack: errorInfo.componentStack,
        timestamp: new Date().toISOString(),
        url: window.location.href,
        userAgent: navigator.userAgent,
        // Add any additional context you want to capture
      };

      // Send to your error reporting service
      // await fetch('/api/error-reporting', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(errorReport),
      // });

      console.log('Error reported:', errorReport);
    } catch (reportError) {
      console.warn('Failed to report error:', reportError);
    } finally {
      this.setState({ isReporting: false });
    }
  };

  private handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: '',
      showDetails: false,
    });
  };

  private handleGoHome = () => {
    window.location.href = '/';
  };

  private toggleDetails = () => {
    this.setState(prev => ({ showDetails: !prev.showDetails }));
  };

  private copyErrorDetails = async () => {
    if (!this.state.error || !this.state.errorInfo) return;

    const errorDetails = `
Error ID: ${this.state.errorId}
Error: ${this.state.error.message}
Stack: ${this.state.error.stack}
Component Stack: ${this.state.errorInfo.componentStack}
URL: ${window.location.href}
Timestamp: ${new Date().toISOString()}
    `.trim();

    try {
      await navigator.clipboard.writeText(errorDetails);
      // You could show a toast notification here
      console.log('Error details copied to clipboard');
    } catch (err) {
      console.warn('Failed to copy error details:', err);
    }
  };

  render() {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default error UI
      return (
        <div className={`min-h-screen bg-gray-50 flex items-center justify-center p-4 ${this.props.className || ''}`}>
          <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-center w-16 h-16 mx-auto mb-4 bg-red-100 rounded-full">
              <AlertTriangle className="w-8 h-8 text-red-600" />
            </div>

            <div className="text-center mb-6">
              <h1 className="text-xl font-semibold text-gray-900 mb-2">
                Something went wrong
              </h1>
              <p className="text-gray-600 text-sm">
                We're sorry, but something unexpected happened. Our team has been notified.
              </p>
              {this.state.errorId && (
                <p className="text-xs text-gray-500 mt-2">
                  Error ID: {this.state.errorId}
                </p>
              )}
            </div>

            <div className="space-y-3 mb-6">
              {this.props.showResetButton && (
                <Button
                  onClick={this.handleReset}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                  disabled={this.state.isReporting}
                >
                  <RefreshCw className={`w-4 h-4 mr-2 ${this.state.isReporting ? 'animate-spin' : ''}`} />
                  {this.state.isReporting ? 'Reporting...' : 'Try Again'}
                </Button>
              )}

              {this.props.showHomeButton && (
                <Button
                  onClick={this.handleGoHome}
                  variant="outline"
                  className="w-full"
                >
                  <Home className="w-4 h-4 mr-2" />
                  Go Home
                </Button>
              )}

              {this.props.showReportButton && (
                <Button
                  onClick={this.toggleDetails}
                  variant="ghost"
                  className="w-full"
                >
                  <Bug className="w-4 h-4 mr-2" />
                  {this.state.showDetails ? 'Hide Details' : 'Show Details'}
                </Button>
              )}
            </div>

            {this.state.showDetails && this.state.error && (
              <div className="border-t pt-4">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-sm font-medium text-gray-900">Error Details</h3>
                  <Button
                    onClick={this.copyErrorDetails}
                    variant="ghost"
                    size="sm"
                    className="text-xs"
                  >
                    Copy
                  </Button>
                </div>
                
                <div className="bg-gray-100 rounded p-3 text-xs font-mono text-gray-800 max-h-40 overflow-y-auto">
                  <div className="mb-2">
                    <strong>Message:</strong> {this.state.error.message}
                  </div>
                  {this.state.error.stack && (
                    <div className="mb-2">
                      <strong>Stack:</strong>
                      <pre className="whitespace-pre-wrap break-words">
                        {this.state.error.stack}
                      </pre>
                    </div>
                  )}
                  {this.state.errorInfo?.componentStack && (
                    <div>
                      <strong>Component Stack:</strong>
                      <pre className="whitespace-pre-wrap break-words">
                        {this.state.errorInfo.componentStack}
                      </pre>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// Higher-order component for easier usage
export function withErrorBoundary<P extends object>(
  Component: React.ComponentType<P>,
  errorBoundaryProps?: Omit<Props, 'children'>
) {
  return function WithErrorBoundary(props: P) {
    return (
      <AdvancedErrorBoundary {...errorBoundaryProps}>
        <Component {...props} />
      </AdvancedErrorBoundary>
    );
  };
}

// Hook for functional components to trigger error boundary
export function useErrorBoundary() {
  const throwError = (error: Error) => {
    throw error;
  };

  const throwAsyncError = async (asyncFn: () => Promise<any>) => {
    try {
      return await asyncFn();
    } catch (error) {
      throwError(error instanceof Error ? error : new Error(String(error)));
    }
  };

  return {
    throwError,
    throwAsyncError,
  };
}
