'use client';

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { logger, analyticsService } from '@/lib';
import { Button } from './Button';
import { Card } from './Card';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log error
    logger.error(
      'ErrorBoundary caught an error',
      error,
      {
        componentStack: errorInfo.componentStack,
      }
    );

    // Track error in analytics
    analyticsService.trackError(error, {
      componentStack: errorInfo.componentStack,
    });

    this.setState({
      error,
      errorInfo,
    });

    // Call custom error handler if provided
    this.props.onError?.(error, errorInfo);
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  handleReload = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-screen flex items-center justify-center p-4 bg-gray-50 dark:bg-gray-900">
          <Card className="max-w-2xl w-full">
            <div className="p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="text-4xl">⚠️</div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Algo salió mal
                </h1>
              </div>
              
              <p className="text-gray-600 dark:text-gray-300 mb-4">
                Lo sentimos, ha ocurrido un error inesperado. Por favor, intenta recargar la página.
              </p>

              {this.state.error && (
                <details className="mb-4">
                  <summary className="cursor-pointer text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Detalles del error
                  </summary>
                  <div className="mt-2 p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
                    <p className="text-sm font-mono text-red-800 dark:text-red-300 break-all">
                      {this.state.error.toString()}
                    </p>
                    {this.state.errorInfo && (
                      <pre className="mt-2 text-xs text-red-700 dark:text-red-400 overflow-auto max-h-48">
                        {this.state.errorInfo.componentStack}
                      </pre>
                    )}
                  </div>
                </details>
              )}

              <div className="flex gap-3">
                <Button
                  onClick={this.handleReset}
                  variant="outline"
                >
                  Intentar de nuevo
                </Button>
                <Button
                  onClick={this.handleReload}
                  variant="primary"
                >
                  Recargar página
                </Button>
              </div>
            </div>
          </Card>
        </div>
      );
    }

    return this.props.children;
  }
}
