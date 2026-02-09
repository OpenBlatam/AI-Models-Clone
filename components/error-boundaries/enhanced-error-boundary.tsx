'use client';

import React, { Component, ErrorInfo, ReactNode, useState } from 'react';
import { AdvancedButton, PrimaryButton, SecondaryButton } from '@/components/ui/advanced-button';
import { 
  AlertTriangle, 
  RefreshCw, 
  Home, 
  Bug, 
  X, 
  AlertCircle,
  Info,
  Download,
  Copy,
  ExternalLink
} from 'lucide-react';

export interface EnhancedErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  onRecover?: () => void;
  showDetails?: boolean;
  enableReporting?: boolean;
  reportEndpoint?: string;
  maxRetries?: number;
  retryDelay?: number;
}

export interface EnhancedErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  retryCount: number;
  isReporting: boolean;
  reportSent: boolean;
  showTechnicalDetails: boolean;
}

export class EnhancedErrorBoundary extends Component<
  EnhancedErrorBoundaryProps,
  EnhancedErrorBoundaryState
> {
  constructor(props: EnhancedErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: 0,
      isReporting: false,
      reportSent: false,
      showTechnicalDetails: false,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<EnhancedErrorBoundaryState> {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({
      error,
      errorInfo,
    });

    // Call custom error handler if provided
    this.props.onError?.(error, errorInfo);

    // Log error to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('Error Boundary caught an error:', error, errorInfo);
    }

    // Report error to external service if enabled
    if (this.props.enableReporting) {
      this.reportError(error, errorInfo);
    }
  }

  private reportError = async (error: Error, errorInfo: ErrorInfo) => {
    if (!this.props.reportEndpoint || this.state.reportSent) return;

    this.setState({ isReporting: true });

    try {
      const errorReport = {
        message: error.message,
        stack: error.stack,
        componentStack: errorInfo.componentStack,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        url: window.location.href,
        retryCount: this.state.retryCount,
      };

      const response = await fetch(this.props.reportEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(errorReport),
      });

      if (response.ok) {
        this.setState({ reportSent: true });
      }
    } catch (reportError) {
      console.error('Failed to report error:', reportError);
    } finally {
      this.setState({ isReporting: false });
    }
  };

  private handleRetry = () => {
    const { maxRetries = 3, retryDelay = 1000 } = this.props;
    
    if (this.state.retryCount >= maxRetries) {
      this.handleReset();
      return;
    }

    this.setState(
      (prevState) => ({ retryCount: prevState.retryCount + 1 }),
      () => {
        setTimeout(() => {
          this.setState({
            hasError: false,
            error: null,
            errorInfo: null,
          });
          this.props.onRecover?.();
        }, retryDelay);
      }
    );
  };

  private handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: 0,
      reportSent: false,
      showTechnicalDetails: false,
    });
    this.props.onRecover?.();
  };

  private handleGoHome = () => {
    if (typeof window !== 'undefined') {
      window.location.href = '/';
    }
  };

  private copyErrorDetails = () => {
    const { error, errorInfo } = this.state;
    if (!error || !errorInfo) return;

    const errorText = `
Error: ${error.message}
Stack: ${error.stack}
Component Stack: ${errorInfo.componentStack}
URL: ${window.location.href}
Timestamp: ${new Date().toISOString()}
    `.trim();

    navigator.clipboard.writeText(errorText).then(() => {
      // Could show a toast notification here
      console.log('Error details copied to clipboard');
    });
  };

  private downloadErrorReport = () => {
    const { error, errorInfo } = this.state;
    if (!error || !errorInfo) return;

    const errorReport = {
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href,
    };

    const blob = new Blob([JSON.stringify(errorReport, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `error-report-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  render() {
    if (this.state.hasError) {
      const { fallback, showDetails = false, enableReporting = false } = this.props;
      const { error, errorInfo, retryCount, isReporting, reportSent, showTechnicalDetails } = this.state;

      if (fallback) {
        return fallback;
      }

      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
          <div className="max-w-2xl w-full bg-white rounded-lg shadow-xl p-8">
            {/* Header */}
            <div className="text-center mb-8">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <AlertTriangle className="w-8 h-8 text-red-600" />
              </div>
              <h1 className="text-2xl font-bold text-gray-900 mb-2">
                Something went wrong
              </h1>
              <p className="text-gray-600">
                We encountered an unexpected error. Don't worry, we're working to fix it.
              </p>
            </div>

            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                <div className="flex items-start">
                  <AlertCircle className="w-5 h-5 text-red-500 mt-0.5 mr-3 flex-shrink-0" />
                  <div className="flex-1">
                    <h3 className="text-sm font-medium text-red-800 mb-1">
                      Error Details
                    </h3>
                    <p className="text-sm text-red-700 font-mono">
                      {error.message}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-3 mb-6">
              <PrimaryButton
                onClick={this.handleRetry}
                leftIcon={<RefreshCw className="w-4 h-4" />}
                fullWidth
                disabled={retryCount >= (this.props.maxRetries || 3)}
              >
                {retryCount > 0 ? `Try Again (${retryCount}/${this.props.maxRetries || 3})` : 'Try Again'}
              </PrimaryButton>
              
              <SecondaryButton
                onClick={this.handleGoHome}
                leftIcon={<Home className="w-4 h-4" />}
                fullWidth
              >
                Go Home
              </SecondaryButton>
            </div>

            {/* Additional Actions */}
            <div className="flex flex-wrap gap-2 mb-6">
              <AdvancedButton
                size="sm"
                variant="ghost"
                onClick={() => this.setState(prev => ({ showTechnicalDetails: !prev.showTechnicalDetails }))}
                leftIcon={<Bug className="w-4 h-4" />}
              >
                {showTechnicalDetails ? 'Hide' : 'Show'} Technical Details
              </AdvancedButton>

              <AdvancedButton
                size="sm"
                variant="ghost"
                onClick={this.copyErrorDetails}
                leftIcon={<Copy className="w-4 h-4" />}
              >
                Copy Details
              </AdvancedButton>

              <AdvancedButton
                size="sm"
                variant="ghost"
                onClick={this.downloadErrorReport}
                leftIcon={<Download className="w-4 h-4" />}
              >
                Download Report
              </AdvancedButton>
            </div>

            {/* Technical Details */}
            {showTechnicalDetails && errorInfo && (
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-6">
                <h3 className="text-sm font-medium text-gray-900 mb-3 flex items-center">
                  <Info className="w-4 h-4 mr-2" />
                  Technical Information
                </h3>
                <div className="space-y-3">
                  <div>
                    <h4 className="text-xs font-medium text-gray-700 mb-1">Component Stack:</h4>
                    <pre className="text-xs text-gray-600 bg-white p-2 rounded border overflow-x-auto">
                      {errorInfo.componentStack}
                    </pre>
                  </div>
                  {error?.stack && (
                    <div>
                      <h4 className="text-xs font-medium text-gray-700 mb-1">Error Stack:</h4>
                      <pre className="text-xs text-gray-600 bg-white p-2 rounded border overflow-x-auto">
                        {error.stack}
                      </pre>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Error Reporting Status */}
            {enableReporting && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <Info className="w-4 h-4 text-blue-500 mr-2" />
                    <span className="text-sm text-blue-700">
                      {isReporting 
                        ? 'Reporting error...' 
                        : reportSent 
                          ? 'Error reported successfully' 
                          : 'Help us improve by reporting this error'
                      }
                    </span>
                  </div>
                  {reportSent && (
                    <div className="text-xs text-blue-600 bg-blue-100 px-2 py-1 rounded">
                      ✓ Reported
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Help Section */}
            <div className="border-t pt-6 mt-6">
              <h3 className="text-sm font-medium text-gray-900 mb-3">Need Help?</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <AdvancedButton
                  size="sm"
                  variant="outline"
                  onClick={() => window.open('/support', '_blank')}
                  rightIcon={<ExternalLink className="w-4 h-4" />}
                  fullWidth
                >
                  Contact Support
                </AdvancedButton>
                <AdvancedButton
                  size="sm"
                  variant="outline"
                  onClick={() => window.open('/docs', '_blank')}
                  rightIcon={<ExternalLink className="w-4 h-4" />}
                  fullWidth
                >
                  View Documentation
                </AdvancedButton>
              </div>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// HOC for wrapping components with error boundary
export function withEnhancedErrorBoundary<P extends object>(
  Component: React.ComponentType<P>,
  errorBoundaryProps?: Omit<EnhancedErrorBoundaryProps, 'children'>
) {
  return function WrappedComponent(props: P) {
    return (
      <EnhancedErrorBoundary {...errorBoundaryProps}>
        <Component {...props} />
      </EnhancedErrorBoundary>
    );
  };
}

// Hook for functional components to trigger errors
export function useEnhancedErrorBoundary() {
  const [error, setError] = useState<Error | null>(null);

  const triggerError = (error: Error) => {
    setError(error);
  };

  const clearError = () => {
    setError(null);
  };

  if (error) {
    throw error;
  }

  return { triggerError, clearError };
}
