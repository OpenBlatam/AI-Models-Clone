declare const __DEV__: boolean;

export interface AnalyticsEvent {
  name: string;
  properties?: Record<string, any>;
  timestamp?: number;
  userId?: string;
  sessionId?: string;
}

export interface AnalyticsUser {
  id: string;
  properties?: Record<string, any>;
}

export interface AnalyticsSession {
  id: string;
  startTime: number;
  endTime?: number;
  duration?: number;
  events: AnalyticsEvent[];
}

class AnalyticsService {
  private static instance: AnalyticsService;
  private isEnabled: boolean = true;
  private currentUser: AnalyticsUser | null = null;
  private currentSession: AnalyticsSession | null = null;
  private eventQueue: AnalyticsEvent[] = [];
  private flushInterval: number = 30000; // 30 seconds
  private maxQueueSize: number = 100;

  private constructor() {
    this.startSession();
    this.startFlushTimer();
  }

  static getInstance(): AnalyticsService {
    if (!AnalyticsService.instance) {
      AnalyticsService.instance = new AnalyticsService();
    }
    return AnalyticsService.instance;
  }

  enable(): void {
    this.isEnabled = true;
  }

  disable(): void {
    this.isEnabled = false;
  }

  setUser(user: AnalyticsUser): void {
    this.currentUser = user;
    this.track('user_identified', { userId: user.id, ...user.properties });
  }

  clearUser(): void {
    this.currentUser = null;
  }

  private startSession(): void {
    this.currentSession = {
      id: this.generateSessionId(),
      startTime: Date.now(),
      events: [],
    };
    this.track('session_started');
  }

  private endSession(): void {
    if (this.currentSession) {
      this.currentSession.endTime = Date.now();
      this.currentSession.duration = this.currentSession.endTime - this.currentSession.startTime;
      this.track('session_ended', { duration: this.currentSession.duration });
    }
  }

  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  track(eventName: string, properties?: Record<string, any>): void {
    if (!this.isEnabled) return;

    const event: AnalyticsEvent = {
      name: eventName,
      properties: {
        ...properties,
        timestamp: Date.now(),
        sessionId: this.currentSession?.id,
        userId: this.currentUser?.id,
      },
      timestamp: Date.now(),
      userId: this.currentUser?.id,
      sessionId: this.currentSession?.id,
    };

    this.eventQueue.push(event);
    this.currentSession?.events.push(event);

    // Flush if queue is full
    if (this.eventQueue.length >= this.maxQueueSize) {
      this.flush();
    }

    // Log in development
    if (__DEV__) {
      console.log('Analytics Event:', event);
    }
  }

  // Screen tracking
  trackScreen(screenName: string, properties?: Record<string, any>): void {
    this.track('screen_view', {
      screen_name: screenName,
      ...properties,
    });
  }

  // User action tracking
  trackAction(actionName: string, properties?: Record<string, any>): void {
    this.track('user_action', {
      action_name: actionName,
      ...properties,
    });
  }

  // Error tracking
  trackError(error: Error, properties?: Record<string, any>): void {
    this.track('error', {
      error_message: error.message,
      error_stack: error.stack,
      ...properties,
    });
  }

  // Performance tracking
  trackPerformance(metricName: string, value: number, properties?: Record<string, any>): void {
    this.track('performance', {
      metric_name: metricName,
      value,
      ...properties,
    });
  }

  // Feature usage tracking
  trackFeatureUsage(featureName: string, properties?: Record<string, any>): void {
    this.track('feature_used', {
      feature_name: featureName,
      ...properties,
    });
  }

  // Conversion tracking
  trackConversion(conversionName: string, value?: number, properties?: Record<string, any>): void {
    this.track('conversion', {
      conversion_name: conversionName,
      value,
      ...properties,
    });
  }

  private startFlushTimer(): void {
    setInterval(() => {
      this.flush();
    }, this.flushInterval);
  }

  private async flush(): Promise<void> {
    if (this.eventQueue.length === 0) return;

    const eventsToSend = [...this.eventQueue];
    this.eventQueue = [];

    try {
      await this.sendEvents(eventsToSend);
    } catch (error) {
      console.error('Analytics flush failed:', error);
      // Re-add events to queue if send failed
      this.eventQueue.unshift(...eventsToSend);
    }
  }

  private async sendEvents(events: AnalyticsEvent[]): Promise<void> {
    // In a real implementation, you would send these to your analytics service
    // Examples: Firebase Analytics, Mixpanel, Amplitude, etc.
    
    const payload = {
      events,
      user: this.currentUser,
      session: this.currentSession,
      timestamp: Date.now(),
    };

    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 100));
    
    if (__DEV__) {
      console.log('Analytics Events Sent:', payload);
    }
  }

  // Get analytics data for debugging
  getAnalyticsData(): {
    user: AnalyticsUser | null;
    session: AnalyticsSession | null;
    queueLength: number;
    isEnabled: boolean;
  } {
    return {
      user: this.currentUser,
      session: this.currentSession,
      queueLength: this.eventQueue.length,
      isEnabled: this.isEnabled,
    };
  }

  // Force flush events
  forceFlush(): Promise<void> {
    return this.flush();
  }

  // Cleanup on app exit
  cleanup(): void {
    this.endSession();
    this.flush();
  }
}

export const analytics = AnalyticsService.getInstance();

// Convenience functions
export const trackEvent = (eventName: string, properties?: Record<string, any>): void => {
  analytics.track(eventName, properties);
};

export const trackScreen = (screenName: string, properties?: Record<string, any>): void => {
  analytics.trackScreen(screenName, properties);
};

export const trackAction = (actionName: string, properties?: Record<string, any>): void => {
  analytics.trackAction(actionName, properties);
};

export const trackError = (error: Error, properties?: Record<string, any>): void => {
  analytics.trackError(error, properties);
};

export const trackPerformance = (metricName: string, value: number, properties?: Record<string, any>): void => {
  analytics.trackPerformance(metricName, value, properties);
};

export const trackFeatureUsage = (featureName: string, properties?: Record<string, any>): void => {
  analytics.trackFeatureUsage(featureName, properties);
};

export const trackConversion = (conversionName: string, value?: number, properties?: Record<string, any>): void => {
  analytics.trackConversion(conversionName, value, properties);
}; 