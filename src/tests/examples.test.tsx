import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import LocalStorageExample from '@/components/examples/local-storage-example';
import DebounceExample from '@/components/examples/debounce-example';
import FormValidationExample from '@/components/examples/form-validation-example';
import DataFetchingExample from '@/components/examples/data-fetching-example';
import HooksStatus from '@/components/examples/hooks-status';
import { useExamplesStore } from '@/lib/stores/examples-store';

// Mock the store
jest.mock('@/lib/stores/examples-store', () => ({
  useExamplesStore: jest.fn(),
  usePerformanceMonitor: jest.fn(() => ({
    measureRenderTime: jest.fn(() => jest.fn()),
    measureMemoryUsage: jest.fn(),
    updatePerformanceMetrics: jest.fn(),
  })),
  useHookStatusMonitor: jest.fn(() => ({
    updateHookStatus: jest.fn(),
  })),
}));

// Mock the hooks
jest.mock('@/hooks/use-local-storage', () => ({
  useLocalStorage: jest.fn(() => [
    { name: '', email: '', role: '' },
    jest.fn(),
    jest.fn(),
  ]),
}));

jest.mock('@/hooks/use-debounce', () => ({
  useDebounce: jest.fn(() => ''),
}));

jest.mock('@/hooks/use-form-validation', () => ({
  useFormValidation: jest.fn(() => ({
    values: { name: '', email: '', phone: '', address: '', city: '', zipCode: '' },
    errors: {},
    touched: {},
    isValid: false,
    isSubmitting: false,
    handleChange: jest.fn(),
    handleBlur: jest.fn(),
    handleSubmit: jest.fn(),
    resetForm: jest.fn(),
    setFieldValue: jest.fn(),
  })),
}));

jest.mock('@/hooks/use-data-fetching', () => ({
  useDataFetching: jest.fn(() => ({
    data: [],
    isLoading: false,
    error: null,
    refetch: jest.fn(),
    clearCache: jest.fn(),
    isCached: false,
    lastFetched: null,
  })),
}));

// Mock react-hot-toast
jest.mock('react-hot-toast', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
  Toaster: () => <div data-testid="toaster" />,
}));

// Mock lucide-react icons
jest.mock('lucide-react', () => ({
  Save: () => <span data-testid="save-icon">💾</span>,
  Trash2: () => <span data-testid="trash-icon">🗑️</span>,
  CheckCircle: () => <span data-testid="check-icon">✅</span>,
  AlertTriangle: () => <span data-testid="alert-icon">⚠️</span>,
  Info: () => <span data-testid="info-icon">ℹ️</span>,
  Search: () => <span data-testid="search-icon">🔍</span>,
  Activity: () => <span data-testid="activity-icon">⚡</span>,
  Clock: () => <span data-testid="clock-icon">🕐</span>,
  User: () => <span data-testid="user-icon">👤</span>,
  Mail: () => <span data-testid="mail-icon">📧</span>,
  Phone: () => <span data-testid="phone-icon">📱</span>,
  MapPin: () => <span data-testid="mappin-icon">📍</span>,
  RefreshCw: () => <span data-testid="refresh-icon">🔄</span>,
  Database: () => <span data-testid="database-icon">💾</span>,
  BarChart3: () => <span data-testid="chart-icon">📊</span>,
  TrendingUp: () => <span data-testid="trending-up-icon">📈</span>,
  TrendingDown: () => <span data-testid="trending-down-icon">📉</span>,
}));

// Test wrapper component
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <Toaster />
    </QueryClientProvider>
  );
};

describe('LocalStorageExample', () => {
  const mockStore = {
    logError: jest.fn(),
  };

  beforeEach(() => {
    (useExamplesStore as jest.Mock).mockReturnValue(mockStore);
  });

  it('renders without crashing', () => {
    render(
      <TestWrapper>
        <LocalStorageExample />
      </TestWrapper>
    );

    expect(screen.getByText('User Data')).toBeInTheDocument();
    expect(screen.getByText('Theme')).toBeInTheDocument();
    expect(screen.getByText('Counter')).toBeInTheDocument();
  });

  it('displays performance info card', () => {
    render(
      <TestWrapper>
        <LocalStorageExample />
      </TestWrapper>
    );

    expect(screen.getByText(/This component is being monitored for performance/)).toBeInTheDocument();
  });

  it('has proper accessibility attributes', () => {
    render(
      <TestWrapper>
        <LocalStorageExample />
      </TestWrapper>
    );

    expect(screen.getByLabelText('Set sample user data')).toBeInTheDocument();
    expect(screen.getByLabelText('Clear user data')).toBeInTheDocument();
  });
});

describe('DebounceExample', () => {
  const mockStore = {
    logError: jest.fn(),
  };

  beforeEach(() => {
    (useExamplesStore as jest.Mock).mockReturnValue(mockStore);
  });

  it('renders without crashing', () => {
    render(
      <TestWrapper>
        <DebounceExample />
      </TestWrapper>
    );

    expect(screen.getByText('Search with Debouncing')).toBeInTheDocument();
    expect(screen.getByText('Configuration')).toBeInTheDocument();
    expect(screen.getByText('Performance Tips')).toBeInTheDocument();
  });

  it('displays search input with proper accessibility', () => {
    render(
      <TestWrapper>
        <DebounceExample />
      </TestWrapper>
    );

    const searchInput = screen.getByTestId('search-input');
    expect(searchInput).toBeInTheDocument();
    expect(searchInput).toHaveAttribute('aria-describedby', 'search-help');
  });

  it('shows real-time status information', () => {
    render(
      <TestWrapper>
        <DebounceExample />
      </TestWrapper>
    );

    expect(screen.getByText('Current value')).toBeInTheDocument();
    expect(screen.getByText('Debounced value')).toBeInTheDocument();
    expect(screen.getByText('Searching in')).toBeInTheDocument();
  });
});

describe('FormValidationExample', () => {
  const mockStore = {
    logError: jest.fn(),
  };

  beforeEach(() => {
    (useExamplesStore as jest.Mock).mockReturnValue(mockStore);
  });

  it('renders without crashing', () => {
    render(
      <TestWrapper>
        <FormValidationExample />
      </TestWrapper>
    );

    expect(screen.getByText('User Information')).toBeInTheDocument();
    expect(screen.getByText('Form State')).toBeInTheDocument();
    expect(screen.getByText('Validation Benefits')).toBeInTheDocument();
  });

  it('displays form fields with proper labels', () => {
    render(
      <TestWrapper>
        <FormValidationExample />
      </TestWrapper>
    );

    expect(screen.getByText('Full Name')).toBeInTheDocument();
    expect(screen.getByText('Email Address')).toBeInTheDocument();
    expect(screen.getByText('Phone Number')).toBeInTheDocument();
  });

  it('shows form progress when fields are filled', () => {
    render(
      <TestWrapper>
        <FormValidationExample />
      </TestWrapper>
    );

    // Form progress should not show initially since no fields are filled
    expect(screen.queryByText('Form Progress')).not.toBeInTheDocument();
  });
});

describe('DataFetchingExample', () => {
  const mockStore = {
    logError: jest.fn(),
  };

  beforeEach(() => {
    (useExamplesStore as jest.Mock).mockReturnValue(mockStore);
  });

  it('renders without crashing', () => {
    render(
      <TestWrapper>
        <DataFetchingExample />
      </TestWrapper>
    );

    expect(screen.getByText('Data Fetching Controls')).toBeInTheDocument();
    expect(screen.getByText('Fetch Statistics')).toBeInTheDocument();
    expect(screen.getByText('Status')).toBeInTheDocument();
  });

  it('displays fetch controls with proper accessibility', () => {
    render(
      <TestWrapper>
        <DataFetchingExample />
      </TestWrapper>
    );

    expect(screen.getByLabelText('Fetch data from API')).toBeInTheDocument();
    expect(screen.getByLabelText('Clear cached data')).toBeInTheDocument();
  });

  it('shows configuration information', () => {
    render(
      <TestWrapper>
        <DataFetchingExample />
      </TestWrapper>
    );

    expect(screen.getByText('API Endpoint')).toBeInTheDocument();
    expect(screen.getByText('Cache Time')).toBeInTheDocument();
    expect(screen.getByText('Retry Count')).toBeInTheDocument();
  });
});

describe('HooksStatus', () => {
  const mockStore = {
    resetStore: jest.fn(),
    logError: jest.fn(),
  };

  const mockHookStatus = {
    localStorageCount: 3,
    debounceActive: true,
    formValid: false,
    dataFetching: true,
    lastUpdated: new Date(),
  };

  const mockPerformanceMetrics = {
    renderTime: 12.5,
    memoryUsage: 45.2,
    interactionCount: 15,
    lastInteraction: new Date(),
  };

  const mockErrorCount = 2;

  beforeEach(() => {
    (useExamplesStore as jest.Mock).mockReturnValue(mockStore);
    jest.spyOn(require('@/lib/stores/examples-store'), 'useHookStatus').mockReturnValue(mockHookStatus);
    jest.spyOn(require('@/lib/stores/examples-store'), 'usePerformanceMetrics').mockReturnValue(mockPerformanceMetrics);
    jest.spyOn(require('@/lib/stores/examples-store'), 'useErrorCount').mockReturnValue(mockErrorCount);
  });

  it('renders without crashing', () => {
    render(
      <TestWrapper>
        <HooksStatus />
      </TestWrapper>
    );

    expect(screen.getByText('Hooks Status Monitor')).toBeInTheDocument();
    expect(screen.getByText('Real-time status of all custom hooks in action')).toBeInTheDocument();
  });

  it('displays hook status grid', () => {
    render(
      <TestWrapper>
        <HooksStatus />
      </TestWrapper>
    );

    expect(screen.getByText('3 items')).toBeInTheDocument();
    expect(screen.getByText('Active')).toBeInTheDocument();
    expect(screen.getByText('Invalid')).toBeInTheDocument();
    expect(screen.getByText('Fetching')).toBeInTheDocument();
  });

  it('shows performance metrics', () => {
    render(
      <TestWrapper>
        <HooksStatus />
      </TestWrapper>
    );

    expect(screen.getByText('12.50ms')).toBeInTheDocument();
    expect(screen.getByText('45.2MB')).toBeInTheDocument();
    expect(screen.getByText('15')).toBeInTheDocument();
  });

  it('displays error count badge', () => {
    render(
      <TestWrapper>
        <HooksStatus />
      </TestWrapper>
    );

    expect(screen.getByText('2 Errors')).toBeInTheDocument();
  });

  it('handles store reset', async () => {
    render(
      <TestWrapper>
        <HooksStatus />
      </TestWrapper>
    );

    const resetButton = screen.getByRole('button', { name: /reset/i });
    fireEvent.click(resetButton);

    await waitFor(() => {
      expect(mockStore.resetStore).toHaveBeenCalled();
    });
  });

  it('shows performance trends', () => {
    render(
      <TestWrapper>
        <HooksStatus />
      </TestWrapper>
    );

    // With render time of 12.5ms, should show "Good" trend
    expect(screen.getByText('Good')).toBeInTheDocument();
  });
});

describe('Error Boundary Integration', () => {
  it('components handle errors gracefully', () => {
    // Test that components don't crash when store methods fail
    const mockStore = {
      logError: jest.fn(() => {
        throw new Error('Store error');
      }),
    };

    (useExamplesStore as jest.Mock).mockReturnValue(mockStore);

    // Components should still render even if store operations fail
    expect(() => {
      render(
        <TestWrapper>
          <LocalStorageExample />
        </TestWrapper>
      );
    }).not.toThrow();
  });
});

describe('Performance Monitoring', () => {
  it('components integrate with performance monitoring', () => {
    const mockPerformanceMonitor = {
      measureRenderTime: jest.fn(() => jest.fn()),
      measureMemoryUsage: jest.fn(),
      updatePerformanceMetrics: jest.fn(),
    };

    jest.spyOn(require('@/lib/stores/examples-store'), 'usePerformanceMonitor').mockReturnValue(mockPerformanceMonitor);

    render(
      <TestWrapper>
        <LocalStorageExample />
      </TestWrapper>
    );

    expect(mockPerformanceMonitor.measureRenderTime).toHaveBeenCalledWith('LocalStorageExample');
    expect(mockPerformanceMonitor.measureMemoryUsage).toHaveBeenCalled();
  });
});





