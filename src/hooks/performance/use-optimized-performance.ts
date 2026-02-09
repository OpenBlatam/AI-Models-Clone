import { useCallback, useRef, useEffect, useMemo, useState } from 'react';
import { InteractionManager, Platform, AppState, AppStateStatus } from 'react-native';

// ============================================================================
// TYPES
// ============================================================================

interface PerformanceMetrics {
  renderCount: number;
  lastRenderTime: number;
  averageRenderTime: number;
  totalRenderTime: number;
  memoryUsage?: number;
  fps?: number;
  interactionCount: number;
  averageInteractionTime: number;
}

interface PerformanceConfig {
  enableRenderTracking: boolean;
  enableMemoryTracking: boolean;
  enableFPSTracking: boolean;
  enableInteractionTracking: boolean;
  maxRenderHistory: number;
  performanceThreshold: number;
  fpsThreshold: number;
  memoryThreshold: number;
}

interface PerformanceOptimization {
  shouldOptimize: boolean;
  optimizationLevel: 'low' | 'medium' | 'high';
  recommendations: string[];
  criticalIssues: string[];
}

interface InteractionTracker {
  startTime: number;
  endTime?: number;
  duration?: number;
  type: string;
  metadata?: Record<string, any>;
}

// ============================================================================
// STATIC CONFIGURATION
// ============================================================================

const DEFAULT_CONFIG: PerformanceConfig = {
  enableRenderTracking: true,
  enableMemoryTracking: false,
  enableFPSTracking: false,
  enableInteractionTracking: true,
  maxRenderHistory: 10,
  performanceThreshold: 16, // 60 FPS threshold
  fpsThreshold: 50,
  memoryThreshold: 100 * 1024 * 1024, // 100MB
};

// ============================================================================
// PERFORMANCE TRACKER CLASS
// ============================================================================

class PerformanceTracker {
  private renderHistory: number[] = [];
  private interactionHistory: InteractionTracker[] = [];
  private fpsHistory: number[] = [];
  private lastFrameTime = Date.now();
  private frameCount = 0;
  private config: PerformanceConfig;

  constructor(config: PerformanceConfig) {
    this.config = config;
  }

  trackRender(renderTime: number): void {
    if (!this.config.enableRenderTracking) return;
    
    this.renderHistory.push(renderTime);
    if (this.renderHistory.length > this.config.maxRenderHistory) {
      this.renderHistory.shift();
    }
  }

  trackInteraction(type: string, metadata?: Record<string, any>): InteractionTracker {
    if (!this.config.enableInteractionTracking) {
      return { startTime: Date.now(), type, metadata };
    }
    
    const interaction: InteractionTracker = {
      startTime: Date.now(),
      type,
      metadata,
    };
    this.interactionHistory.push(interaction);
    return interaction;
  }

  endInteraction(interaction: InteractionTracker): void {
    if (!this.config.enableInteractionTracking) return;
    
    interaction.endTime = Date.now();
    interaction.duration = interaction.endTime - interaction.startTime;
  }

  trackFPS(): void {
    if (!this.config.enableFPSTracking) return;
    
    const now = Date.now();
    this.frameCount++;
    
    if (now - this.lastFrameTime >= 1000) {
      const fps = Math.round((this.frameCount * 1000) / (now - this.lastFrameTime));
      this.fpsHistory.push(fps);
      
      if (this.fpsHistory.length > 60) {
        this.fpsHistory.shift();
      }
      
      this.frameCount = 0;
      this.lastFrameTime = now;
    }
  }

  getMetrics(): PerformanceMetrics {
    const renderCount = this.renderHistory.length;
    const lastRenderTime = this.renderHistory[renderCount - 1] || 0;
    const totalRenderTime = this.renderHistory.reduce((sum, time) => sum + time, 0);
    const averageRenderTime = renderCount > 0 ? totalRenderTime / renderCount : 0;

    const interactionCount = this.interactionHistory.length;
    const completedInteractions = this.interactionHistory.filter(i => i.duration !== undefined);
    const averageInteractionTime = completedInteractions.length > 0 
      ? completedInteractions.reduce((sum, i) => sum + (i.duration || 0), 0) / completedInteractions.length
      : 0;

    return {
      renderCount,
      lastRenderTime,
      averageRenderTime,
      totalRenderTime,
      fps: this.fpsHistory.length > 0 
        ? this.fpsHistory.reduce((sum, fps) => sum + fps, 0) / this.fpsHistory.length 
        : undefined,
      interactionCount,
      averageInteractionTime,
    };
  }

  getOptimizationRecommendations(): PerformanceOptimization {
    const metrics = this.getMetrics();
    const recommendations: string[] = [];
    const criticalIssues: string[] = [];
    let optimizationLevel: 'low' | 'medium' | 'high' = 'low';

    // Render time analysis
    if (metrics.averageRenderTime > this.config.performanceThreshold) {
      recommendations.push('Consider using React.memo for expensive components');
      recommendations.push('Implement useMemo and useCallback for expensive calculations');
      optimizationLevel = 'medium';
    }

    if (metrics.averageRenderTime > this.config.performanceThreshold * 2) {
      criticalIssues.push('Component rendering is taking too long');
      recommendations.push('Consider implementing virtualization for long lists');
      recommendations.push('Profile component tree for performance bottlenecks');
      optimizationLevel = 'high';
    }

    // FPS analysis
    if (metrics.fps && metrics.fps < this.config.fpsThreshold) {
      criticalIssues.push('FPS is below optimal threshold');
      recommendations.push('Check for heavy operations on main thread');
      recommendations.push('Consider using InteractionManager for non-critical operations');
      optimizationLevel = 'high';
    }

    // Render count analysis
    if (metrics.renderCount > this.config.maxRenderHistory * 0.8) {
      recommendations.push('High render count detected - check for unnecessary re-renders');
      recommendations.push('Review component dependencies and state updates');
      optimizationLevel = 'medium';
    }

    // Interaction analysis
    if (metrics.averageInteractionTime > 100) {
      recommendations.push('User interactions are taking too long to respond');
      recommendations.push('Consider debouncing or throttling user input handlers');
      optimizationLevel = 'medium';
    }

    return {
      shouldOptimize: optimizationLevel !== 'low',
      optimizationLevel,
      recommendations,
      criticalIssues,
    };
  }

  clearHistory(): void {
    this.renderHistory = [];
    this.interactionHistory = [];
    this.fpsHistory = [];
  }
}

// ============================================================================
// MAIN HOOK
// ============================================================================

export function useOptimizedPerformance(config: Partial<PerformanceConfig> = {}): {
  metrics: PerformanceMetrics;
  optimization: PerformanceOptimization;
  trackRender: () => void;
  trackInteraction: (type: string, metadata?: Record<string, any>) => InteractionTracker;
  endInteraction: (interaction: InteractionTracker) => void;
  clearHistory: () => void;
  isAppActive: boolean;
  deferOperation: (operation: () => void) => void;
  batchOperations: (operations: (() => void)[]) => void;
} {
  const finalConfig = useMemo(() => ({ ...DEFAULT_CONFIG, ...config }), [config]);
  
  const tracker = useRef(new PerformanceTracker(finalConfig));
  const renderStartTime = useRef<number>(0);
  const [metrics, setMetrics] = useState<PerformanceMetrics>(tracker.current.getMetrics());
  const [isAppActive, setIsAppActive] = useState(AppState.currentState === 'active');

  // App state tracking
  useEffect(() => {
    const handleAppStateChange = (nextAppState: AppStateStatus) => {
      setIsAppActive(nextAppState === 'active');
    };

    const subscription = AppState.addEventListener('change', handleAppStateChange);
    return () => subscription?.remove();
  }, []);

  // FPS tracking
  useEffect(() => {
    if (!finalConfig.enableFPSTracking) return;

    let animationFrameId: number;
    
    const trackFPS = () => {
      tracker.current.trackFPS();
      animationFrameId = requestAnimationFrame(trackFPS);
    };

    if (isAppActive) {
      trackFPS();
    }

    return () => {
      if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
      }
    };
  }, [finalConfig.enableFPSTracking, isAppActive]);

  // Render tracking
  const trackRender = useCallback(() => {
    if (!finalConfig.enableRenderTracking) return;

    const renderTime = Date.now() - renderStartTime.current;
    tracker.current.trackRender(renderTime);
    
    // Update metrics
    setMetrics(tracker.current.getMetrics());
    
    // Reset start time for next render
    renderStartTime.current = Date.now();
  }, [finalConfig.enableRenderTracking]);

  // Interaction tracking
  const trackInteraction = useCallback((type: string, metadata?: Record<string, any>): InteractionTracker => {
    if (!finalConfig.enableInteractionTracking) {
      return { startTime: Date.now(), type, metadata };
    }
    
    return tracker.current.trackInteraction(type, metadata);
  }, [finalConfig.enableInteractionTracking]);

  const endInteraction = useCallback((interaction: InteractionTracker) => {
    if (!finalConfig.enableInteractionTracking) return;
    
    tracker.current.endInteraction(interaction);
    setMetrics(tracker.current.getMetrics());
  }, [finalConfig.enableInteractionTracking]);

  // History clearing
  const clearHistory = useCallback(() => {
    tracker.current.clearHistory();
    setMetrics(tracker.current.getMetrics());
  }, []);

  // Performance optimization utilities
  const deferOperation = useCallback((operation: () => void) => {
    if (Platform.OS === 'ios') {
      InteractionManager.runAfterInteractions(() => {
        operation();
      });
    } else {
      requestAnimationFrame(() => {
        operation();
      });
    }
  }, []);

  const batchOperations = useCallback((operations: (() => void)[]) => {
    if (Platform.OS === 'ios') {
      InteractionManager.runAfterInteractions(() => {
        operations.forEach(operation => operation());
      });
    } else {
      requestAnimationFrame(() => {
        operations.forEach(operation => operation());
      });
    }
  }, []);

  // Start tracking render time
  useEffect(() => {
    renderStartTime.current = Date.now();
  });

  // Get optimization recommendations
  const optimization = useMemo(() => 
    tracker.current.getOptimizationRecommendations(), 
    [metrics]
  );

  return {
    metrics,
    optimization,
    trackRender,
    trackInteraction,
    endInteraction,
    clearHistory,
    isAppActive,
    deferOperation,
    batchOperations,
  };
}

// ============================================================================
// SPECIALIZED HOOKS
// ============================================================================

export function useRenderOptimization(componentName: string): {
  shouldRender: boolean;
  trackRender: () => void;
  renderCount: number;
} {
  const { trackRender, metrics } = useOptimizedPerformance();
  const lastRenderTime = useRef<number>(0);
  const [shouldRender, setShouldRender] = useState(true);

  const optimizedTrackRender = useCallback(() => {
    const now = Date.now();
    const timeSinceLastRender = now - lastRenderTime.current;
    
    // Only render if enough time has passed (throttling)
    if (timeSinceLastRender > 16) { // 60 FPS threshold
      setShouldRender(true);
      lastRenderTime.current = now;
      trackRender();
    } else {
      setShouldRender(false);
    }
  }, [trackRender]);

  return {
    shouldRender,
    trackRender: optimizedTrackRender,
    renderCount: metrics.renderCount,
  };
}

export function useInteractionOptimization(): {
  trackUserInteraction: (type: string, metadata?: Record<string, any>) => void;
  getInteractionMetrics: () => InteractionTracker[];
  averageInteractionTime: number;
} {
  const { trackInteraction, endInteraction, metrics } = useOptimizedPerformance();
  const activeInteractions = useRef<Map<string, InteractionTracker>>(new Map());

  const trackUserInteraction = useCallback((type: string, metadata?: Record<string, any>) => {
    const interaction = trackInteraction(type, metadata);
    activeInteractions.current.set(type, interaction);
    
    // Auto-end interaction after a reasonable timeout
    setTimeout(() => {
      const activeInteraction = activeInteractions.current.get(type);
      if (activeInteraction) {
        endInteraction(activeInteraction);
        activeInteractions.current.delete(type);
      }
    }, 5000); // 5 second timeout
  }, [trackInteraction, endInteraction]);

  const getInteractionMetrics = useCallback(() => {
    return Array.from(activeInteractions.current.values());
  }, []);

  return {
    trackUserInteraction,
    getInteractionMetrics,
    averageInteractionTime: metrics.averageInteractionTime,
  };
}

export function useMemoryOptimization(): {
  memoryUsage: number | undefined;
  shouldOptimizeMemory: boolean;
  clearMemory: () => void;
  memoryPressure: 'low' | 'medium' | 'high';
} {
  const { metrics, optimization } = useOptimizedPerformance({
    enableMemoryTracking: true,
  });

  const shouldOptimizeMemory = useMemo(() => {
    // This would typically check actual memory usage
    // For now, we'll use render metrics as a proxy
    return metrics.renderCount > 50 || metrics.averageRenderTime > 20;
  }, [metrics]);

  const memoryPressure = useMemo(() => {
    if (metrics.renderCount > 100 || metrics.averageRenderTime > 30) {
      return 'high';
    } else if (metrics.renderCount > 50 || metrics.averageRenderTime > 20) {
      return 'medium';
    }
    return 'low';
  }, [metrics]);

  const clearMemory = useCallback(() => {
    // This would typically clear caches, images, etc.
    console.log('Memory optimization triggered');
  }, []);

  return {
    memoryUsage: metrics.memoryUsage,
    shouldOptimizeMemory,
    clearMemory,
    memoryPressure,
  };
}
import { InteractionManager, Platform, AppState, AppStateStatus } from 'react-native';

// ============================================================================
// TYPES
// ============================================================================

interface PerformanceMetrics {
  renderCount: number;
  lastRenderTime: number;
  averageRenderTime: number;
  totalRenderTime: number;
  memoryUsage?: number;
  fps?: number;
  interactionCount: number;
  averageInteractionTime: number;
}

interface PerformanceConfig {
  enableRenderTracking: boolean;
  enableMemoryTracking: boolean;
  enableFPSTracking: boolean;
  enableInteractionTracking: boolean;
  maxRenderHistory: number;
  performanceThreshold: number;
  fpsThreshold: number;
  memoryThreshold: number;
}

interface PerformanceOptimization {
  shouldOptimize: boolean;
  optimizationLevel: 'low' | 'medium' | 'high';
  recommendations: string[];
  criticalIssues: string[];
}

interface InteractionTracker {
  startTime: number;
  endTime?: number;
  duration?: number;
  type: string;
  metadata?: Record<string, any>;
}

// ============================================================================
// STATIC CONFIGURATION
// ============================================================================

const DEFAULT_CONFIG: PerformanceConfig = {
  enableRenderTracking: true,
  enableMemoryTracking: false,
  enableFPSTracking: false,
  enableInteractionTracking: true,
  maxRenderHistory: 10,
  performanceThreshold: 16, // 60 FPS threshold
  fpsThreshold: 50,
  memoryThreshold: 100 * 1024 * 1024, // 100MB
};

// ============================================================================
// PERFORMANCE TRACKER CLASS
// ============================================================================

class PerformanceTracker {
  private renderHistory: number[] = [];
  private interactionHistory: InteractionTracker[] = [];
  private fpsHistory: number[] = [];
  private lastFrameTime = Date.now();
  private frameCount = 0;
  private config: PerformanceConfig;

  constructor(config: PerformanceConfig) {
    this.config = config;
  }

  trackRender(renderTime: number): void {
    if (!this.config.enableRenderTracking) return;
    
    this.renderHistory.push(renderTime);
    if (this.renderHistory.length > this.config.maxRenderHistory) {
      this.renderHistory.shift();
    }
  }

  trackInteraction(type: string, metadata?: Record<string, any>): InteractionTracker {
    if (!this.config.enableInteractionTracking) {
      return { startTime: Date.now(), type, metadata };
    }
    
    const interaction: InteractionTracker = {
      startTime: Date.now(),
      type,
      metadata,
    };
    this.interactionHistory.push(interaction);
    return interaction;
  }

  endInteraction(interaction: InteractionTracker): void {
    if (!this.config.enableInteractionTracking) return;
    
    interaction.endTime = Date.now();
    interaction.duration = interaction.endTime - interaction.startTime;
  }

  trackFPS(): void {
    if (!this.config.enableFPSTracking) return;
    
    const now = Date.now();
    this.frameCount++;
    
    if (now - this.lastFrameTime >= 1000) {
      const fps = Math.round((this.frameCount * 1000) / (now - this.lastFrameTime));
      this.fpsHistory.push(fps);
      
      if (this.fpsHistory.length > 60) {
        this.fpsHistory.shift();
      }
      
      this.frameCount = 0;
      this.lastFrameTime = now;
    }
  }

  getMetrics(): PerformanceMetrics {
    const renderCount = this.renderHistory.length;
    const lastRenderTime = this.renderHistory[renderCount - 1] || 0;
    const totalRenderTime = this.renderHistory.reduce((sum, time) => sum + time, 0);
    const averageRenderTime = renderCount > 0 ? totalRenderTime / renderCount : 0;

    const interactionCount = this.interactionHistory.length;
    const completedInteractions = this.interactionHistory.filter(i => i.duration !== undefined);
    const averageInteractionTime = completedInteractions.length > 0 
      ? completedInteractions.reduce((sum, i) => sum + (i.duration || 0), 0) / completedInteractions.length
      : 0;

    return {
      renderCount,
      lastRenderTime,
      averageRenderTime,
      totalRenderTime,
      fps: this.fpsHistory.length > 0 
        ? this.fpsHistory.reduce((sum, fps) => sum + fps, 0) / this.fpsHistory.length 
        : undefined,
      interactionCount,
      averageInteractionTime,
    };
  }

  getOptimizationRecommendations(): PerformanceOptimization {
    const metrics = this.getMetrics();
    const recommendations: string[] = [];
    const criticalIssues: string[] = [];
    let optimizationLevel: 'low' | 'medium' | 'high' = 'low';

    // Render time analysis
    if (metrics.averageRenderTime > this.config.performanceThreshold) {
      recommendations.push('Consider using React.memo for expensive components');
      recommendations.push('Implement useMemo and useCallback for expensive calculations');
      optimizationLevel = 'medium';
    }

    if (metrics.averageRenderTime > this.config.performanceThreshold * 2) {
      criticalIssues.push('Component rendering is taking too long');
      recommendations.push('Consider implementing virtualization for long lists');
      recommendations.push('Profile component tree for performance bottlenecks');
      optimizationLevel = 'high';
    }

    // FPS analysis
    if (metrics.fps && metrics.fps < this.config.fpsThreshold) {
      criticalIssues.push('FPS is below optimal threshold');
      recommendations.push('Check for heavy operations on main thread');
      recommendations.push('Consider using InteractionManager for non-critical operations');
      optimizationLevel = 'high';
    }

    // Render count analysis
    if (metrics.renderCount > this.config.maxRenderHistory * 0.8) {
      recommendations.push('High render count detected - check for unnecessary re-renders');
      recommendations.push('Review component dependencies and state updates');
      optimizationLevel = 'medium';
    }

    // Interaction analysis
    if (metrics.averageInteractionTime > 100) {
      recommendations.push('User interactions are taking too long to respond');
      recommendations.push('Consider debouncing or throttling user input handlers');
      optimizationLevel = 'medium';
    }

    return {
      shouldOptimize: optimizationLevel !== 'low',
      optimizationLevel,
      recommendations,
      criticalIssues,
    };
  }

  clearHistory(): void {
    this.renderHistory = [];
    this.interactionHistory = [];
    this.fpsHistory = [];
  }
}

// ============================================================================
// MAIN HOOK
// ============================================================================

export function useOptimizedPerformance(config: Partial<PerformanceConfig> = {}): {
  metrics: PerformanceMetrics;
  optimization: PerformanceOptimization;
  trackRender: () => void;
  trackInteraction: (type: string, metadata?: Record<string, any>) => InteractionTracker;
  endInteraction: (interaction: InteractionTracker) => void;
  clearHistory: () => void;
  isAppActive: boolean;
  deferOperation: (operation: () => void) => void;
  batchOperations: (operations: (() => void)[]) => void;
} {
  const finalConfig = useMemo(() => ({ ...DEFAULT_CONFIG, ...config }), [config]);
  
  const tracker = useRef(new PerformanceTracker(finalConfig));
  const renderStartTime = useRef<number>(0);
  const [metrics, setMetrics] = useState<PerformanceMetrics>(tracker.current.getMetrics());
  const [isAppActive, setIsAppActive] = useState(AppState.currentState === 'active');

  // App state tracking
  useEffect(() => {
    const handleAppStateChange = (nextAppState: AppStateStatus) => {
      setIsAppActive(nextAppState === 'active');
    };

    const subscription = AppState.addEventListener('change', handleAppStateChange);
    return () => subscription?.remove();
  }, []);

  // FPS tracking
  useEffect(() => {
    if (!finalConfig.enableFPSTracking) return;

    let animationFrameId: number;
    
    const trackFPS = () => {
      tracker.current.trackFPS();
      animationFrameId = requestAnimationFrame(trackFPS);
    };

    if (isAppActive) {
      trackFPS();
    }

    return () => {
      if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
      }
    };
  }, [finalConfig.enableFPSTracking, isAppActive]);

  // Render tracking
  const trackRender = useCallback(() => {
    if (!finalConfig.enableRenderTracking) return;

    const renderTime = Date.now() - renderStartTime.current;
    tracker.current.trackRender(renderTime);
    
    // Update metrics
    setMetrics(tracker.current.getMetrics());
    
    // Reset start time for next render
    renderStartTime.current = Date.now();
  }, [finalConfig.enableRenderTracking]);

  // Interaction tracking
  const trackInteraction = useCallback((type: string, metadata?: Record<string, any>): InteractionTracker => {
    if (!finalConfig.enableInteractionTracking) {
      return { startTime: Date.now(), type, metadata };
    }
    
    return tracker.current.trackInteraction(type, metadata);
  }, [finalConfig.enableInteractionTracking]);

  const endInteraction = useCallback((interaction: InteractionTracker) => {
    if (!finalConfig.enableInteractionTracking) return;
    
    tracker.current.endInteraction(interaction);
    setMetrics(tracker.current.getMetrics());
  }, [finalConfig.enableInteractionTracking]);

  // History clearing
  const clearHistory = useCallback(() => {
    tracker.current.clearHistory();
    setMetrics(tracker.current.getMetrics());
  }, []);

  // Performance optimization utilities
  const deferOperation = useCallback((operation: () => void) => {
    if (Platform.OS === 'ios') {
      InteractionManager.runAfterInteractions(() => {
        operation();
      });
    } else {
      requestAnimationFrame(() => {
        operation();
      });
    }
  }, []);

  const batchOperations = useCallback((operations: (() => void)[]) => {
    if (Platform.OS === 'ios') {
      InteractionManager.runAfterInteractions(() => {
        operations.forEach(operation => operation());
      });
    } else {
      requestAnimationFrame(() => {
        operations.forEach(operation => operation());
      });
    }
  }, []);

  // Start tracking render time
  useEffect(() => {
    renderStartTime.current = Date.now();
  });

  // Get optimization recommendations
  const optimization = useMemo(() => 
    tracker.current.getOptimizationRecommendations(), 
    [metrics]
  );

  return {
    metrics,
    optimization,
    trackRender,
    trackInteraction,
    endInteraction,
    clearHistory,
    isAppActive,
    deferOperation,
    batchOperations,
  };
}

// ============================================================================
// SPECIALIZED HOOKS
// ============================================================================

export function useRenderOptimization(componentName: string): {
  shouldRender: boolean;
  trackRender: () => void;
  renderCount: number;
} {
  const { trackRender, metrics } = useOptimizedPerformance();
  const lastRenderTime = useRef<number>(0);
  const [shouldRender, setShouldRender] = useState(true);

  const optimizedTrackRender = useCallback(() => {
    const now = Date.now();
    const timeSinceLastRender = now - lastRenderTime.current;
    
    // Only render if enough time has passed (throttling)
    if (timeSinceLastRender > 16) { // 60 FPS threshold
      setShouldRender(true);
      lastRenderTime.current = now;
      trackRender();
    } else {
      setShouldRender(false);
    }
  }, [trackRender]);

  return {
    shouldRender,
    trackRender: optimizedTrackRender,
    renderCount: metrics.renderCount,
  };
}

export function useInteractionOptimization(): {
  trackUserInteraction: (type: string, metadata?: Record<string, any>) => void;
  getInteractionMetrics: () => InteractionTracker[];
  averageInteractionTime: number;
} {
  const { trackInteraction, endInteraction, metrics } = useOptimizedPerformance();
  const activeInteractions = useRef<Map<string, InteractionTracker>>(new Map());

  const trackUserInteraction = useCallback((type: string, metadata?: Record<string, any>) => {
    const interaction = trackInteraction(type, metadata);
    activeInteractions.current.set(type, interaction);
    
    // Auto-end interaction after a reasonable timeout
    setTimeout(() => {
      const activeInteraction = activeInteractions.current.get(type);
      if (activeInteraction) {
        endInteraction(activeInteraction);
        activeInteractions.current.delete(type);
      }
    }, 5000); // 5 second timeout
  }, [trackInteraction, endInteraction]);

  const getInteractionMetrics = useCallback(() => {
    return Array.from(activeInteractions.current.values());
  }, []);

  return {
    trackUserInteraction,
    getInteractionMetrics,
    averageInteractionTime: metrics.averageInteractionTime,
  };
}

export function useMemoryOptimization(): {
  memoryUsage: number | undefined;
  shouldOptimizeMemory: boolean;
  clearMemory: () => void;
  memoryPressure: 'low' | 'medium' | 'high';
} {
  const { metrics, optimization } = useOptimizedPerformance({
    enableMemoryTracking: true,
  });

  const shouldOptimizeMemory = useMemo(() => {
    // This would typically check actual memory usage
    // For now, we'll use render metrics as a proxy
    return metrics.renderCount > 50 || metrics.averageRenderTime > 20;
  }, [metrics]);

  const memoryPressure = useMemo(() => {
    if (metrics.renderCount > 100 || metrics.averageRenderTime > 30) {
      return 'high';
    } else if (metrics.renderCount > 50 || metrics.averageRenderTime > 20) {
      return 'medium';
    }
    return 'low';
  }, [metrics]);

  const clearMemory = useCallback(() => {
    // This would typically clear caches, images, etc.
    console.log('Memory optimization triggered');
  }, []);

  return {
    memoryUsage: metrics.memoryUsage,
    shouldOptimizeMemory,
    clearMemory,
    memoryPressure,
  };
}


