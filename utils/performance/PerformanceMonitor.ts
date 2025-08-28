import { InteractionManager } from 'react-native';

export interface PerformanceMetric {
  name: string;
  startTime: number;
  endTime?: number;
  duration?: number;
  metadata?: Record<string, any>;
}

export interface PerformanceReport {
  metrics: PerformanceMetric[];
  totalDuration: number;
  averageDuration: number;
  slowestOperation: PerformanceMetric | null;
  fastestOperation: PerformanceMetric | null;
}

class PerformanceMonitor {
  private static instance: PerformanceMonitor;
  private metrics: Map<string, PerformanceMetric> = new Map();
  private isEnabled: boolean = __DEV__;

  private constructor() {}

  static getInstance(): PerformanceMonitor {
    if (!PerformanceMonitor.instance) {
      PerformanceMonitor.instance = new PerformanceMonitor();
    }
    return PerformanceMonitor.instance;
  }

  enable(): void {
    this.isEnabled = true;
  }

  disable(): void {
    this.isEnabled = false;
  }

  startTimer(name: string, metadata?: Record<string, any>): void {
    if (!this.isEnabled) return;

    const metric: PerformanceMetric = {
      name,
      startTime: performance.now(),
      metadata,
    };

    this.metrics.set(name, metric);
  }

  endTimer(name: string): void {
    if (!this.isEnabled) return;

    const metric = this.metrics.get(name);
    if (!metric) {
      console.warn(`PerformanceMonitor: Timer "${name}" was not started`);
      return;
    }

    metric.endTime = performance.now();
    metric.duration = metric.endTime - metric.startTime;

    if (metric.duration > 100) {
      console.warn(`PerformanceMonitor: Slow operation detected: ${name} took ${metric.duration.toFixed(2)}ms`);
    }
  }

  measureAsync<T>(name: string, operation: () => Promise<T>, metadata?: Record<string, any>): Promise<T> {
    if (!this.isEnabled) {
      return operation();
    }

    this.startTimer(name, metadata);
    return operation().finally(() => {
      this.endTimer(name);
    });
  }

  measureSync<T>(name: string, operation: () => T, metadata?: Record<string, any>): T {
    if (!this.isEnabled) {
      return operation();
    }

    this.startTimer(name, metadata);
    try {
      const result = operation();
      this.endTimer(name);
      return result;
    } catch (error) {
      this.endTimer(name);
      throw error;
    }
  }

  measureInteraction(name: string, operation: () => void, metadata?: Record<string, any>): void {
    if (!this.isEnabled) {
      operation();
      return;
    }

    this.startTimer(name, metadata);
    InteractionManager.runAfterInteractions(() => {
      operation();
      this.endTimer(name);
    });
  }

  getReport(): PerformanceReport {
    const completedMetrics = Array.from(this.metrics.values()).filter(m => m.duration !== undefined);
    
    if (completedMetrics.length === 0) {
      return {
        metrics: [],
        totalDuration: 0,
        averageDuration: 0,
        slowestOperation: null,
        fastestOperation: null,
      };
    }

    const totalDuration = completedMetrics.reduce((sum, m) => sum + (m.duration || 0), 0);
    const averageDuration = totalDuration / completedMetrics.length;
    const slowestOperation = completedMetrics.reduce((slowest, current) => 
      (current.duration || 0) > (slowest.duration || 0) ? current : slowest
    );
    const fastestOperation = completedMetrics.reduce((fastest, current) => 
      (current.duration || 0) < (fastest.duration || 0) ? current : fastest
    );

    return {
      metrics: completedMetrics,
      totalDuration,
      averageDuration,
      slowestOperation,
      fastestOperation,
    };
  }

  clearMetrics(): void {
    this.metrics.clear();
  }

  logReport(): void {
    if (!this.isEnabled) return;

    const report = this.getReport();
    console.group('Performance Report');
    console.log(`Total Operations: ${report.metrics.length}`);
    console.log(`Total Duration: ${report.totalDuration.toFixed(2)}ms`);
    console.log(`Average Duration: ${report.averageDuration.toFixed(2)}ms`);
    
    if (report.slowestOperation) {
      console.log(`Slowest: ${report.slowestOperation.name} (${report.slowestOperation.duration?.toFixed(2)}ms)`);
    }
    
    if (report.fastestOperation) {
      console.log(`Fastest: ${report.fastestOperation.name} (${report.fastestOperation.duration?.toFixed(2)}ms)`);
    }
    
    console.groupEnd();
  }
}

export const performanceMonitor = PerformanceMonitor.getInstance();

// Convenience functions
export const measureAsync = <T>(name: string, operation: () => Promise<T>, metadata?: Record<string, any>): Promise<T> => {
  return performanceMonitor.measureAsync(name, operation, metadata);
};

export const measureSync = <T>(name: string, operation: () => T, metadata?: Record<string, any>): T => {
  return performanceMonitor.measureSync(name, operation, metadata);
};

export const measureInteraction = (name: string, operation: () => void, metadata?: Record<string, any>): void => {
  return performanceMonitor.measureInteraction(name, operation, metadata);
}; 