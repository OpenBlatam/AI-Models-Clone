import '@testing-library/jest-dom';
import { jest } from '@jest/globals';

// Mock Next.js router
jest.mock('next/router', () => ({
  useRouter() {
    return {
      route: '/',
      pathname: '/',
      query: {},
      asPath: '/',
      push: jest.fn(),
      pop: jest.fn(),
      reload: jest.fn(),
      back: jest.fn(),
      prefetch: jest.fn(),
      beforePopState: jest.fn(),
      events: {
        on: jest.fn(),
        off: jest.fn(),
        emit: jest.fn(),
      },
      isFallback: false,
      isLocaleDomain: false,
      isReady: true,
      defaultLocale: 'en',
      domainLocales: [],
      isPreview: false,
    };
  },
}));

// Mock Next.js navigation
jest.mock('next/navigation', () => ({
  useRouter() {
    return {
      push: jest.fn(),
      replace: jest.fn(),
      prefetch: jest.fn(),
      back: jest.fn(),
      forward: jest.fn(),
      refresh: jest.fn(),
    };
  },
  useSearchParams() {
    return new URLSearchParams();
  },
  usePathname() {
    return '/';
  },
}));

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock;

// Mock sessionStorage
const sessionStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.sessionStorage = sessionStorageMock;

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock IntersectionObserver
global.IntersectionObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

// Mock ResizeObserver
global.ResizeObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

// Mock Performance API
Object.defineProperty(window, 'performance', {
  writable: true,
  value: {
    now: jest.fn(() => Date.now()),
    getEntriesByType: jest.fn(() => []),
    mark: jest.fn(),
    measure: jest.fn(),
    clearMarks: jest.fn(),
    clearMeasures: jest.fn(),
  },
});

// Mock fetch
global.fetch = jest.fn();

// Mock console methods in tests
const originalConsoleError = console.error;
const originalConsoleWarn = console.warn;

beforeAll(() => {
  console.error = (...args: any[]) => {
    if (
      typeof args[0] === 'string' &&
      args[0].includes('Warning: ReactDOM.render is no longer supported')
    ) {
      return;
    }
    originalConsoleError.call(console, ...args);
  };
  
  console.warn = (...args: any[]) => {
    if (
      typeof args[0] === 'string' &&
      args[0].includes('Warning: componentWillReceiveProps has been renamed')
    ) {
      return;
    }
    originalConsoleWarn.call(console, ...args);
  };
});

afterAll(() => {
  console.error = originalConsoleError;
  console.warn = originalConsoleWarn;
});

// Clean up after each test
afterEach(() => {
  jest.clearAllMocks();
  localStorageMock.clear();
  sessionStorageMock.clear();
});

// Global test utilities
global.testUtils = {
  // Mock data generators
  createMockUser: (overrides = {}) => ({
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

  createMockApiResponse: <T>(data: T, overrides = {}) => ({
    success: true,
    data,
    message: 'Success',
    ...overrides,
  }),

  createMockPaginatedResponse: <T>(data: T[], overrides = {}) => ({
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

  // Wait for async operations
  waitFor: (ms: number) => new Promise(resolve => setTimeout(resolve, ms)),

  // Mock API calls
  mockApiCall: (response: any, delay = 0) => {
    return new Promise(resolve => {
      setTimeout(() => resolve(response), delay);
    });
  },

  // Create test environment
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
expect.extend({
  toHaveBeenCalledWithMatch(received: jest.Mock, expected: any) {
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

  toBeValidDate(received: any) {
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
});

// Type declarations for global test utilities
declare global {
  namespace jest {
    interface Matchers<R> {
      toHaveBeenCalledWithMatch(expected: any): R;
      toBeValidDate(): R;
    }
  }
  
  var testUtils: {
    createMockUser: (overrides?: any) => any;
    createMockApiResponse: <T>(data: T, overrides?: any) => any;
    createMockPaginatedResponse: <T>(data: T[], overrides?: any) => any;
    waitFor: (ms: number) => Promise<void>;
    mockApiCall: (response: any, delay?: number) => Promise<any>;
    createTestEnvironment: () => { restore: () => void };
  };
}

export {};
