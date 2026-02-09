import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react-native';
import { ErrorBoundary, useErrorHandler } from '../../components/error-boundary/error-boundary';

// Mock component that throws an error
const ThrowError = ({ shouldThrow }: { shouldThrow: boolean }) => {
  if (shouldThrow) {
    throw new Error('Test error');
  }
  return <div>No error</div>;
};

describe('ErrorBoundary', () => {
  beforeEach(() => {
    // Suppress console.error for tests
    jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('renders children when there is no error', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={false} />
      </ErrorBoundary>
    );

    expect(screen.getByText('No error')).toBeTruthy();
  });

  it('renders error fallback when there is an error', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    expect(screen.getByText('Oops! Something went wrong')).toBeTruthy();
    expect(screen.getByText('Try Again')).toBeTruthy();
    expect(screen.getByText('Report Issue')).toBeTruthy();
  });

  it('calls onError callback when error occurs', () => {
    const onError = jest.fn();
    
    render(
      <ErrorBoundary onError={onError}>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    expect(onError).toHaveBeenCalledWith(
      expect.any(Error),
      expect.objectContaining({
        componentStack: expect.any(String),
      })
    );
  });

  it('retries when retry button is pressed', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    expect(screen.getByText('Oops! Something went wrong')).toBeTruthy();

    fireEvent.press(screen.getByText('Try Again'));

    // After retry, the error boundary should reset and render children again
    expect(screen.getByText('No error')).toBeTruthy();
  });

  it('shows error details in development mode', () => {
    const originalEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = 'development';

    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    expect(screen.getByText('Error Details (Development Only)')).toBeTruthy();
    expect(screen.getByText('Test error')).toBeTruthy();

    process.env.NODE_ENV = originalEnv;
  });
});

describe('useErrorHandler', () => {
  it('handles errors correctly', () => {
    const TestComponent = () => {
      const { handleError } = useErrorHandler();
      
      const triggerError = () => {
        handleError(new Error('Test error'), 'test context');
      };

      return (
        <div>
          <button onPress={triggerError}>Trigger Error</button>
        </div>
      );
    };

    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    
    render(<TestComponent />);
    
    fireEvent.press(screen.getByText('Trigger Error'));
    
    expect(consoleSpy).toHaveBeenCalledWith(
      'Error in test context:',
      expect.objectContaining({
        message: 'Test error',
        platform: 'react-native',
      })
    );

    consoleSpy.mockRestore();
  });
});
import { render, screen, fireEvent } from '@testing-library/react-native';
import { ErrorBoundary, useErrorHandler } from '../../components/error-boundary/error-boundary';

// Mock component that throws an error
const ThrowError = ({ shouldThrow }: { shouldThrow: boolean }) => {
  if (shouldThrow) {
    throw new Error('Test error');
  }
  return <div>No error</div>;
};

describe('ErrorBoundary', () => {
  beforeEach(() => {
    // Suppress console.error for tests
    jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('renders children when there is no error', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={false} />
      </ErrorBoundary>
    );

    expect(screen.getByText('No error')).toBeTruthy();
  });

  it('renders error fallback when there is an error', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    expect(screen.getByText('Oops! Something went wrong')).toBeTruthy();
    expect(screen.getByText('Try Again')).toBeTruthy();
    expect(screen.getByText('Report Issue')).toBeTruthy();
  });

  it('calls onError callback when error occurs', () => {
    const onError = jest.fn();
    
    render(
      <ErrorBoundary onError={onError}>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    expect(onError).toHaveBeenCalledWith(
      expect.any(Error),
      expect.objectContaining({
        componentStack: expect.any(String),
      })
    );
  });

  it('retries when retry button is pressed', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    expect(screen.getByText('Oops! Something went wrong')).toBeTruthy();

    fireEvent.press(screen.getByText('Try Again'));

    // After retry, the error boundary should reset and render children again
    expect(screen.getByText('No error')).toBeTruthy();
  });

  it('shows error details in development mode', () => {
    const originalEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = 'development';

    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    expect(screen.getByText('Error Details (Development Only)')).toBeTruthy();
    expect(screen.getByText('Test error')).toBeTruthy();

    process.env.NODE_ENV = originalEnv;
  });
});

describe('useErrorHandler', () => {
  it('handles errors correctly', () => {
    const TestComponent = () => {
      const { handleError } = useErrorHandler();
      
      const triggerError = () => {
        handleError(new Error('Test error'), 'test context');
      };

      return (
        <div>
          <button onPress={triggerError}>Trigger Error</button>
        </div>
      );
    };

    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    
    render(<TestComponent />);
    
    fireEvent.press(screen.getByText('Trigger Error'));
    
    expect(consoleSpy).toHaveBeenCalledWith(
      'Error in test context:',
      expect.objectContaining({
        message: 'Test error',
        platform: 'react-native',
      })
    );

    consoleSpy.mockRestore();
  });
});


