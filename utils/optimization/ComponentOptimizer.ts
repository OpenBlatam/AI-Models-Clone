import React, { ComponentType, memo, useMemo, useCallback } from 'react';
import { performanceMonitor } from '../performance/PerformanceMonitor';

export interface ComponentOptimizationConfig {
  enableMemoization: boolean;
  enableCallbackOptimization: boolean;
  enableRenderOptimization: boolean;
  enablePropsOptimization: boolean;
  enableStateOptimization: boolean;
  maxRenderTime: number; // ms
  maxReRenderCount: number;
  enableAutoOptimization: boolean;
}

export interface ComponentMetrics {
  renderTime: number;
  reRenderCount: number;
  propsChangeCount: number;
  stateChangeCount: number;
  memoryUsage: number;
  optimizationScore: number;
}

export interface OptimizedComponentConfig {
  shouldMemoize: boolean;
  shouldOptimizeCallbacks: boolean;
  shouldOptimizeProps: boolean;
  shouldOptimizeState: boolean;
  customOptimizations: string[];
}

class ComponentOptimizer {
  private static instance: ComponentOptimizer;
  private config: ComponentOptimizationConfig;
  private componentMetrics: Map<string, ComponentMetrics> = new Map();
  private optimizationHistory: Map<string, string[]> = new Map();

  private constructor() {
    this.config = {
      enableMemoization: true,
      enableCallbackOptimization: true,
      enableRenderOptimization: true,
      enablePropsOptimization: true,
      enableStateOptimization: true,
      maxRenderTime: 16, // 60fps target
      maxReRenderCount: 10,
      enableAutoOptimization: true,
    };
  }

  static getInstance(): ComponentOptimizer {
    if (!ComponentOptimizer.instance) {
      ComponentOptimizer.instance = new ComponentOptimizer();
    }
    return ComponentOptimizer.instance;
  }

  // Configuration management
  getConfig(): ComponentOptimizationConfig {
    return { ...this.config };
  }

  updateConfig(newConfig: Partial<ComponentOptimizationConfig>): void {
    this.config = { ...this.config, ...newConfig };
  }

  // Component memoization
  memoizeComponent<T extends object>(
    Component: ComponentType<T>,
    componentName: string,
    options?: { customProps?: (props: T) => any }
  ): ComponentType<T> {
    if (!this.config.enableMemoization) {
      return Component;
    }

    const MemoizedComponent = memo(Component, (prevProps, nextProps) => {
      // Custom comparison function
      if (options?.customProps) {
        const prevCustom = options.customProps(prevProps);
        const nextCustom = options.customProps(nextProps);
        return JSON.stringify(prevCustom) === JSON.stringify(nextCustom);
      }

      // Default shallow comparison
      return false; // Always re-render for now, implement proper comparison
    });

    // Track component optimization
    this.trackComponentOptimization(componentName, 'memoization');

    return MemoizedComponent;
  }

  // Callback optimization
  optimizeCallback<T extends (...args: any[]) => any>(
    callback: T,
    dependencies: any[],
    componentName: string
  ): T {
    if (!this.config.enableCallbackOptimization) {
      return callback;
    }

    const optimizedCallback = useCallback(callback, dependencies);

    // Track callback optimization
    this.trackComponentOptimization(componentName, 'callback_optimization');

    return optimizedCallback;
  }

  // Props optimization
  optimizeProps<T extends object>(
    props: T,
    componentName: string,
    optimizationKeys?: (keyof T)[]
  ): T {
    if (!this.config.enablePropsOptimization) {
      return props;
    }

    const optimizedProps = useMemo(() => {
      if (optimizationKeys) {
        const optimized: Partial<T> = {};
        optimizationKeys.forEach(key => {
          optimized[key] = props[key];
        });
        return optimized as T;
      }
      return props;
    }, [props, optimizationKeys]);

    // Track props optimization
    this.trackComponentOptimization(componentName, 'props_optimization');

    return optimizedProps;
  }

  // State optimization
  optimizeState<T>(
    initialState: T,
    componentName: string,
    optimizationConfig?: {
      shouldFreeze?: boolean;
      shouldDeepClone?: boolean;
    }
  ): T {
    if (!this.config.enableStateOptimization) {
      return initialState;
    }

    const optimizedState = useMemo(() => {
      let state = initialState;

      if (optimizationConfig?.shouldDeepClone) {
        state = JSON.parse(JSON.stringify(initialState));
      }

      if (optimizationConfig?.shouldFreeze) {
        state = Object.freeze(state);
      }

      return state;
    }, [initialState]);

    // Track state optimization
    this.trackComponentOptimization(componentName, 'state_optimization');

    return optimizedState;
  }

  // Render optimization
  optimizeRender<T extends object>(
    Component: ComponentType<T>,
    componentName: string,
    renderConfig?: {
      shouldBatchUpdates?: boolean;
      shouldDebounceRenders?: boolean;
      shouldThrottleRenders?: boolean;
    }
  ): ComponentType<T> {
    if (!this.config.enableRenderOptimization) {
      return Component;
    }

    const OptimizedComponent = (props: T) => {
      const renderTime = performanceMonitor.measureSync(
        `${componentName}_render`,
        () => {
          return React.createElement(Component, props);
        }
      );

      // Track render metrics
      this.updateComponentMetrics(componentName, { renderTime });

      return React.createElement(Component, props);
    };

    // Track render optimization
    this.trackComponentOptimization(componentName, 'render_optimization');

    return OptimizedComponent;
  }

  // Auto-optimization
  autoOptimizeComponent<T extends object>(
    Component: ComponentType<T>,
    componentName: string,
    autoConfig?: OptimizedComponentConfig
  ): ComponentType<T> {
    if (!this.config.enableAutoOptimization) {
      return Component;
    }

    let optimizedComponent = Component;

    // Apply memoization if enabled
    if (autoConfig?.shouldMemoize ?? this.config.enableMemoization) {
      optimizedComponent = this.memoizeComponent(optimizedComponent, componentName);
    }

    // Apply render optimization if enabled
    if (this.config.enableRenderOptimization) {
      optimizedComponent = this.optimizeRender(optimizedComponent, componentName);
    }

    // Track auto-optimization
    this.trackComponentOptimization(componentName, 'auto_optimization');

    return optimizedComponent;
  }

  // Performance monitoring
  trackComponentMetrics(componentName: string, metrics: Partial<ComponentMetrics>): void {
    const currentMetrics = this.componentMetrics.get(componentName) || {
      renderTime: 0,
      reRenderCount: 0,
      propsChangeCount: 0,
      stateChangeCount: 0,
      memoryUsage: 0,
      optimizationScore: 0,
    };

    this.componentMetrics.set(componentName, {
      ...currentMetrics,
      ...metrics,
    });
  }

  private updateComponentMetrics(componentName: string, metrics: Partial<ComponentMetrics>): void {
    this.trackComponentMetrics(componentName, metrics);
  }

  private trackComponentOptimization(componentName: string, optimizationType: string): void {
    const history = this.optimizationHistory.get(componentName) || [];
    history.push(optimizationType);
    this.optimizationHistory.set(componentName, history);
  }

  // Component analysis
  analyzeComponent(componentName: string): {
    metrics: ComponentMetrics;
    optimizations: string[];
    recommendations: string[];
  } {
    const metrics = this.componentMetrics.get(componentName);
    const optimizations = this.optimizationHistory.get(componentName) || [];

    const recommendations: string[] = [];

    if (metrics) {
      if (metrics.renderTime > this.config.maxRenderTime) {
        recommendations.push('Consider memoization to reduce render time');
      }

      if (metrics.reRenderCount > this.config.maxReRenderCount) {
        recommendations.push('Optimize props and state to reduce re-renders');
      }

      if (metrics.propsChangeCount > 5) {
        recommendations.push('Consider optimizing props structure');
      }

      if (metrics.stateChangeCount > 10) {
        recommendations.push('Consider optimizing state updates');
      }
    }

    return {
      metrics: metrics || {
        renderTime: 0,
        reRenderCount: 0,
        propsChangeCount: 0,
        stateChangeCount: 0,
        memoryUsage: 0,
        optimizationScore: 0,
      },
      optimizations,
      recommendations,
    };
  }

  // Batch optimization
  optimizeComponentBatch(components: Array<{
    component: ComponentType<any>;
    name: string;
    config?: OptimizedComponentConfig;
  }>): Map<string, ComponentType<any>> {
    const optimizedComponents = new Map<string, ComponentType<any>>();

    for (const { component, name, config } of components) {
      const optimized = this.autoOptimizeComponent(component, name, config);
      optimizedComponents.set(name, optimized);
    }

    return optimizedComponents;
  }

  // Generate optimization report
  generateComponentReport(): string {
    let report = 'Component Optimization Report\n';
    report += '=============================\n\n';

    for (const [componentName, metrics] of this.componentMetrics) {
      const analysis = this.analyzeComponent(componentName);

      report += `Component: ${componentName}\n`;
      report += `  Render Time: ${metrics.renderTime.toFixed(2)}ms\n`;
      report += `  Re-render Count: ${metrics.reRenderCount}\n`;
      report += `  Props Changes: ${metrics.propsChangeCount}\n`;
      report += `  State Changes: ${metrics.stateChangeCount}\n`;
      report += `  Memory Usage: ${(metrics.memoryUsage / 1024).toFixed(2)}KB\n`;
      report += `  Optimization Score: ${metrics.optimizationScore.toFixed(2)}/100\n\n`;

      if (analysis.optimizations.length > 0) {
        report += `  Applied Optimizations:\n`;
        analysis.optimizations.forEach(opt => {
          report += `    - ${opt}\n`;
        });
        report += '\n';
      }

      if (analysis.recommendations.length > 0) {
        report += `  Recommendations:\n`;
        analysis.recommendations.forEach(rec => {
          report += `    - ${rec}\n`;
        });
        report += '\n';
      }
    }

    return report;
  }

  // Get component metrics
  getComponentMetrics(componentName: string): ComponentMetrics | undefined {
    return this.componentMetrics.get(componentName);
  }

  // Get all component metrics
  getAllComponentMetrics(): Map<string, ComponentMetrics> {
    return new Map(this.componentMetrics);
  }

  // Clear metrics
  clearMetrics(): void {
    this.componentMetrics.clear();
    this.optimizationHistory.clear();
  }

  // Optimization utilities
  createOptimizedComponent<T extends object>(
    Component: ComponentType<T>,
    componentName: string,
    config?: OptimizedComponentConfig
  ): ComponentType<T> {
    return this.autoOptimizeComponent(Component, componentName, config);
  }

  createMemoizedComponent<T extends object>(
    Component: ComponentType<T>,
    componentName: string,
    customProps?: (props: T) => any
  ): ComponentType<T> {
    return this.memoizeComponent(Component, componentName, { customProps });
  }

  createOptimizedCallback<T extends (...args: any[]) => any>(
    callback: T,
    dependencies: any[],
    componentName: string
  ): T {
    return this.optimizeCallback(callback, dependencies, componentName);
  }
}

export const componentOptimizer = ComponentOptimizer.getInstance();

// Convenience functions
export const optimizeComponent = <T extends object>(
  Component: ComponentType<T>,
  componentName: string,
  config?: OptimizedComponentConfig
): ComponentType<T> => {
  return componentOptimizer.autoOptimizeComponent(Component, componentName, config);
};

export const memoizeComponent = <T extends object>(
  Component: ComponentType<T>,
  componentName: string,
  customProps?: (props: T) => any
): ComponentType<T> => {
  return componentOptimizer.memoizeComponent(Component, componentName, { customProps });
};

export const optimizeCallback = <T extends (...args: any[]) => any>(
  callback: T,
  dependencies: any[],
  componentName: string
): T => {
  return componentOptimizer.optimizeCallback(callback, dependencies, componentName);
};

export const analyzeComponent = (componentName: string) => {
  return componentOptimizer.analyzeComponent(componentName);
};

export const generateComponentReport = (): string => {
  return componentOptimizer.generateComponentReport();
}; 