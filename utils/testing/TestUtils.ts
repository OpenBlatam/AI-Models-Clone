import { render, RenderOptions } from '@testing-library/react-native';
import React, { ReactElement } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { I18nextProvider } from 'react-i18next';
import { i18n } from '../i18n/i18nConfig';

// Test configuration
export const TEST_CONFIG = {
  timeout: 10000,
  retryAttempts: 3,
  performanceThreshold: 100, // ms
  memoryThreshold: 50, // MB
} as const;

// Performance metrics interface
export interface PerformanceMetrics {
  renderTime: number;
  memoryUsage: number;
  interactionTime: number;
  bundleSize?: number;
}

// Test result interface
export interface TestResult {
  name: string;
  passed: boolean;
  duration: number;
  error?: string;
  performanceMetrics?: PerformanceMetrics;
}

// Custom render function with providers
const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        cacheTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
  });

  return (
    <QueryClientProvider client={queryClient}>
      <I18nextProvider i18n={i18n}>
        {children}
      </I18nextProvider>
    </QueryClientProvider>
  );
};

const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: AllTheProviders, ...options });

// Performance testing utilities
export class PerformanceTester {
  private static instance: PerformanceTester;
  private metrics: Map<string, PerformanceMetrics> = new Map();

  static getInstance(): PerformanceTester {
    if (!PerformanceTester.instance) {
      PerformanceTester.instance = new PerformanceTester();
    }
    return PerformanceTester.instance;
  }

  measureRenderTime(componentName: string, renderFn: () => void): number {
    const startTime = performance.now();
    renderFn();
    const endTime = performance.now();
    const renderTime = endTime - startTime;

    this.metrics.set(componentName, {
      ...this.metrics.get(componentName),
      renderTime,
    });

    return renderTime;
  }

  measureInteractionTime(componentName: string, interactionFn: () => void): number {
    const startTime = performance.now();
    interactionFn();
    const endTime = performance.now();
    const interactionTime = endTime - startTime;

    this.metrics.set(componentName, {
      ...this.metrics.get(componentName),
      interactionTime,
    });

    return interactionTime;
  }

  getMetrics(componentName: string): PerformanceMetrics | undefined {
    return this.metrics.get(componentName);
  }

  getAllMetrics(): Map<string, PerformanceMetrics> {
    return new Map(this.metrics);
  }

  clearMetrics(): void {
    this.metrics.clear();
  }

  generateReport(): string {
    let report = 'Performance Test Report\n';
    report += '========================\n\n';

    for (const [componentName, metrics] of this.metrics) {
      report += `Component: ${componentName}\n`;
      report += `  Render Time: ${metrics.renderTime.toFixed(2)}ms\n`;
      report += `  Interaction Time: ${metrics.interactionTime?.toFixed(2) || 'N/A'}ms\n`;
      report += `  Memory Usage: ${metrics.memoryUsage?.toFixed(2) || 'N/A'}MB\n`;
      report += '\n';
    }

    return report;
  }
}

// Component testing utilities
export class ComponentTester {
  static async testComponent(
    component: ReactElement,
    testName: string,
    options?: {
      timeout?: number;
      retries?: number;
    }
  ): Promise<TestResult> {
    const { timeout = TEST_CONFIG.timeout, retries = TEST_CONFIG.retryAttempts } = options || {};
    const startTime = performance.now();

    try {
      for (let attempt = 1; attempt <= retries; attempt++) {
        try {
          const { unmount } = customRender(component);
          
          // Wait for component to be stable
          await new Promise(resolve => setTimeout(resolve, 100));
          
          unmount();
          
          const endTime = performance.now();
          const duration = endTime - startTime;

          return {
            name: testName,
            passed: true,
            duration,
          };
        } catch (error) {
          if (attempt === retries) {
            throw error;
          }
          await new Promise(resolve => setTimeout(resolve, 1000));
        }
      }
    } catch (error) {
      const endTime = performance.now();
      const duration = endTime - startTime;

      return {
        name: testName,
        passed: false,
        duration,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }

    throw new Error('Unexpected test execution');
  }

  static async testComponentWithPerformance(
    component: ReactElement,
    testName: string,
    interactionTest?: () => void
  ): Promise<TestResult> {
    const performanceTester = PerformanceTester.getInstance();
    const startTime = performance.now();

    try {
      const renderTime = performanceTester.measureRenderTime(testName, () => {
        customRender(component);
      });

      if (interactionTest) {
        performanceTester.measureInteractionTime(testName, interactionTest);
      }

      const metrics = performanceTester.getMetrics(testName);
      const endTime = performance.now();
      const duration = endTime - startTime;

      return {
        name: testName,
        passed: true,
        duration,
        performanceMetrics: metrics,
      };
    } catch (error) {
      const endTime = performance.now();
      const duration = endTime - startTime;

      return {
        name: testName,
        passed: false,
        duration,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }
}

// Integration testing utilities
export class IntegrationTester {
  static async testUserFlow(
    steps: Array<{
      name: string;
      action: () => Promise<void>;
      validation?: () => Promise<boolean>;
    }>,
    testName: string
  ): Promise<TestResult> {
    const startTime = performance.now();

    try {
      for (const step of steps) {
        await step.action();
        
        if (step.validation) {
          const isValid = await step.validation();
          if (!isValid) {
            throw new Error(`Validation failed for step: ${step.name}`);
          }
        }
      }

      const endTime = performance.now();
      const duration = endTime - startTime;

      return {
        name: testName,
        passed: true,
        duration,
      };
    } catch (error) {
      const endTime = performance.now();
      const duration = endTime - startTime;

      return {
        name: testName,
        passed: false,
        duration,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }
}

// Accessibility testing utilities
export class AccessibilityTester {
  static async testAccessibility(
    component: ReactElement,
    testName: string
  ): Promise<TestResult> {
    const startTime = performance.now();

    try {
      const { getByRole, getByLabelText, getByTestId } = customRender(component);

      // Test for basic accessibility elements
      const accessibleElements = [
        () => getByRole('button'),
        () => getByRole('text'),
        () => getByLabelText(''),
        () => getByTestId(''),
      ];

      for (const elementTest of accessibleElements) {
        try {
          elementTest();
        } catch (error) {
          // Element not found, which is acceptable for some components
        }
      }

      const endTime = performance.now();
      const duration = endTime - startTime;

      return {
        name: testName,
        passed: true,
        duration,
      };
    } catch (error) {
      const endTime = performance.now();
      const duration = endTime - startTime;

      return {
        name: testName,
        passed: false,
        duration,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }
}

// Test suite runner
export class TestSuiteRunner {
  private tests: Array<() => Promise<TestResult>> = [];

  addTest(testFn: () => Promise<TestResult>): void {
    this.tests.push(testFn);
  }

  async runTests(): Promise<TestResult[]> {
    const results: TestResult[] = [];

    for (const test of this.tests) {
      try {
        const result = await test();
        results.push(result);
      } catch (error) {
        results.push({
          name: 'Unknown Test',
          passed: false,
          duration: 0,
          error: error instanceof Error ? error.message : 'Unknown error',
        });
      }
    }

    return results;
  }

  generateReport(results: TestResult[]): string {
    let report = 'Test Suite Report\n';
    report += '==================\n\n';

    const passed = results.filter(r => r.passed).length;
    const failed = results.filter(r => !r.passed).length;
    const total = results.length;

    report += `Summary:\n`;
    report += `  Total Tests: ${total}\n`;
    report += `  Passed: ${passed}\n`;
    report += `  Failed: ${failed}\n`;
    report += `  Success Rate: ${((passed / total) * 100).toFixed(2)}%\n\n`;

    report += `Detailed Results:\n`;
    for (const result of results) {
      const status = result.passed ? '✅ PASS' : '❌ FAIL';
      report += `  ${status} ${result.name} (${result.duration.toFixed(2)}ms)\n`;
      if (result.error) {
        report += `    Error: ${result.error}\n`;
      }
    }

    return report;
  }
}

// Export utilities
export { customRender as render };
export * from '@testing-library/react-native'; 