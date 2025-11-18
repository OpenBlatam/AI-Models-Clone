import { render, RenderOptions } from '@testing-library/react';
import React, { ReactElement } from 'react';
import { useRouter } from 'next/navigation';

// Custom render function with providers
export function renderWithProviders(
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) {
  const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
    return <>{children}</>;
  };

  return render(ui, { wrapper: AllTheProviders, ...options });
}

// Mock Next.js router
export const mockRouter = {
  push: jest.fn(),
  replace: jest.fn(),
  prefetch: jest.fn(),
  back: jest.fn(),
  forward: jest.fn(),
  refresh: jest.fn(),
  pathname: '/',
  query: {},
  asPath: '/',
};

// Mock useRouter hook
export function mockUseRouter(overrides = {}) {
  (useRouter as jest.Mock).mockReturnValue({
    ...mockRouter,
    ...overrides,
  });
}

// Test data factories
export const testData = {
  user: (overrides = {}) => ({
    id: 'user-1',
    email: 'test@example.com',
    name: 'Test User',
    role: 'user' as const,
    isActive: true,
    preferences: {
      theme: 'light' as const,
      language: 'en',
      notifications: {
        email: true,
        push: false,
        sms: false,
        marketing: false,
      },
      privacy: {
        profileVisibility: 'public' as const,
        dataSharing: false,
        analytics: true,
      },
    },
    ...overrides,
  }),

  apiResponse: <T>(data: T, overrides = {}) => ({
    success: true,
    data,
    message: 'Success',
    ...overrides,
  }),

  paginatedResponse: <T>(data: T[], overrides = {}) => ({
    success: true,
    data,
    message: 'Success',
    meta: {
      page: 1,
      limit: 10,
      total: data.length,
      totalPages: Math.ceil(data.length / 10),
      ...overrides.meta,
    },
    ...overrides,
  }),
};

// Async utilities
export const testUtils = {
  waitFor: (ms: number) => new Promise(resolve => setTimeout(resolve, ms)),
  
  mockApiCall: (response: any, delay = 0) => {
    return new Promise(resolve => {
      setTimeout(() => resolve(response), delay);
    });
  },
  
  createTestEnvironment: () => {
    const originalEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = 'test';
    
    return {
      restore: () => {
        process.env.NODE_ENV = originalEnv;
      },
    };
  },
};

// Custom matchers
export const customMatchers = {
  toHaveBeenCalledWithMatch: (received: jest.Mock, expected: any) => {
    const pass = received.mock.calls.some(call =>
      call.some((arg: any) => expect(arg).toMatchObject(expected))
    );
    
    if (pass) {
      return {
        message: () => `expected ${received.getDisplayName()} not to have been called with arguments matching ${JSON.stringify(expected)}`,
        pass: true,
      };
    } else {
      return {
        message: () => `expected ${received.getDisplayName()} to have been called with arguments matching ${JSON.stringify(expected)}`,
        pass: false,
      };
    }
  },

  toBeValidDate: (received: any) => {
    const pass = received instanceof Date && !isNaN(received.getTime());
    
    if (pass) {
      return {
        message: () => `expected ${received} not to be a valid Date`,
        pass: true,
      };
    } else {
      return {
        message: () => `expected ${received} to be a valid Date`,
        pass: false,
      };
    }
  },
};

// Setup and teardown
export const setupTestEnvironment = () => {
  beforeAll(() => {
    // Global test setup
    jest.clearAllMocks();
  });

  afterEach(() => {
    // Clean up after each test
    jest.clearAllMocks();
  });

  afterAll(() => {
    // Global test cleanup
    jest.restoreAllMocks();
  });
};
