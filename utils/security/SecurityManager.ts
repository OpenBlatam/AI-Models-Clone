import AsyncStorage from '@react-native-async-storage/async-storage';
import { Platform } from 'react-native';

export interface SecurityConfig {
  enableEncryption: boolean;
  enableBiometrics: boolean;
  enablePinCode: boolean;
  sessionTimeout: number; // minutes
  maxLoginAttempts: number;
  passwordMinLength: number;
  requireSpecialChars: boolean;
  requireNumbers: boolean;
  requireUppercase: boolean;
}

export interface SecurityEvent {
  type: 'login' | 'logout' | 'failed_login' | 'password_change' | 'security_alert';
  timestamp: number;
  userId?: string;
  details?: Record<string, any>;
}

export interface SecurityMetrics {
  totalLogins: number;
  failedLogins: number;
  securityAlerts: number;
  lastLoginTime?: number;
  sessionDuration: number;
}

class SecurityManager {
  private static instance: SecurityManager;
  private config: SecurityConfig;
  private events: SecurityEvent[] = [];
  private isInitialized: boolean = false;

  private constructor() {
    this.config = {
      enableEncryption: true,
      enableBiometrics: false,
      enablePinCode: false,
      sessionTimeout: 30,
      maxLoginAttempts: 5,
      passwordMinLength: 8,
      requireSpecialChars: true,
      requireNumbers: true,
      requireUppercase: true,
    };
  }

  static getInstance(): SecurityManager {
    if (!SecurityManager.instance) {
      SecurityManager.instance = new SecurityManager();
    }
    return SecurityManager.instance;
  }

  async initialize(): Promise<void> {
    if (this.isInitialized) return;

    try {
      // Load saved configuration
      const savedConfig = await AsyncStorage.getItem('security_config');
      if (savedConfig) {
        this.config = { ...this.config, ...JSON.parse(savedConfig) };
      }

      // Load security events
      const savedEvents = await AsyncStorage.getItem('security_events');
      if (savedEvents) {
        this.events = JSON.parse(savedEvents);
      }

      this.isInitialized = true;
    } catch (error) {
      console.error('SecurityManager initialization failed:', error);
    }
  }

  // Configuration management
  getConfig(): SecurityConfig {
    return { ...this.config };
  }

  async updateConfig(newConfig: Partial<SecurityConfig>): Promise<void> {
    this.config = { ...this.config, ...newConfig };
    await AsyncStorage.setItem('security_config', JSON.stringify(this.config));
  }

  // Password validation
  validatePassword(password: string): { isValid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (password.length < this.config.passwordMinLength) {
      errors.push(`Password must be at least ${this.config.passwordMinLength} characters long`);
    }

    if (this.config.requireUppercase && !/[A-Z]/.test(password)) {
      errors.push('Password must contain at least one uppercase letter');
    }

    if (this.config.requireNumbers && !/\d/.test(password)) {
      errors.push('Password must contain at least one number');
    }

    if (this.config.requireSpecialChars && !/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
      errors.push('Password must contain at least one special character');
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  }

  // Security event tracking
  async logEvent(event: Omit<SecurityEvent, 'timestamp'>): Promise<void> {
    const securityEvent: SecurityEvent = {
      ...event,
      timestamp: Date.now(),
    };

    this.events.push(securityEvent);

    // Keep only last 100 events
    if (this.events.length > 100) {
      this.events = this.events.slice(-100);
    }

    await AsyncStorage.setItem('security_events', JSON.stringify(this.events));

    // Log in development
    if (__DEV__) {
      console.log('Security Event:', securityEvent);
    }
  }

  // Login attempt tracking
  private loginAttempts: Map<string, { count: number; lastAttempt: number }> = new Map();

  async trackLoginAttempt(userId: string, success: boolean): Promise<void> {
    const now = Date.now();
    const attempts = this.loginAttempts.get(userId) || { count: 0, lastAttempt: 0 };

    if (success) {
      this.loginAttempts.delete(userId);
      await this.logEvent({
        type: 'login',
        userId,
        details: { timestamp: now },
      });
    } else {
      attempts.count++;
      attempts.lastAttempt = now;
      this.loginAttempts.set(userId, attempts);

      await this.logEvent({
        type: 'failed_login',
        userId,
        details: { attemptCount: attempts.count, timestamp: now },
      });

      // Check if account should be locked
      if (attempts.count >= this.config.maxLoginAttempts) {
        await this.logEvent({
          type: 'security_alert',
          userId,
          details: { reason: 'max_login_attempts_exceeded', attempts: attempts.count },
        });
      }
    }
  }

  isAccountLocked(userId: string): boolean {
    const attempts = this.loginAttempts.get(userId);
    if (!attempts) return false;

    const timeSinceLastAttempt = Date.now() - attempts.lastAttempt;
    const lockoutDuration = 15 * 60 * 1000; // 15 minutes

    return attempts.count >= this.config.maxLoginAttempts && timeSinceLastAttempt < lockoutDuration;
  }

  // Session management
  private sessions: Map<string, { startTime: number; lastActivity: number }> = new Map();

  startSession(userId: string): void {
    const now = Date.now();
    this.sessions.set(userId, { startTime: now, lastActivity: now });
  }

  updateSessionActivity(userId: string): void {
    const session = this.sessions.get(userId);
    if (session) {
      session.lastActivity = Date.now();
    }
  }

  isSessionValid(userId: string): boolean {
    const session = this.sessions.get(userId);
    if (!session) return false;

    const timeSinceLastActivity = Date.now() - session.lastActivity;
    const sessionTimeoutMs = this.config.sessionTimeout * 60 * 1000;

    return timeSinceLastActivity < sessionTimeoutMs;
  }

  endSession(userId: string): void {
    this.sessions.delete(userId);
    this.logEvent({
      type: 'logout',
      userId,
      details: { timestamp: Date.now() },
    });
  }

  // Security metrics
  getSecurityMetrics(): SecurityMetrics {
    const logins = this.events.filter(e => e.type === 'login').length;
    const failedLogins = this.events.filter(e => e.type === 'failed_login').length;
    const securityAlerts = this.events.filter(e => e.type === 'security_alert').length;
    const lastLogin = this.events
      .filter(e => e.type === 'login')
      .sort((a, b) => b.timestamp - a.timestamp)[0];

    return {
      totalLogins: logins,
      failedLogins,
      securityAlerts,
      lastLoginTime: lastLogin?.timestamp,
      sessionDuration: this.config.sessionTimeout,
    };
  }

  // Data encryption (basic implementation)
  private async encryptData(data: string): Promise<string> {
    // In a real implementation, you would use a proper encryption library
    // This is a basic example - replace with actual encryption
    return btoa(data);
  }

  private async decryptData(encryptedData: string): Promise<string> {
    // In a real implementation, you would use a proper decryption library
    // This is a basic example - replace with actual decryption
    return atob(encryptedData);
  }

  async secureStore(key: string, value: string): Promise<void> {
    if (this.config.enableEncryption) {
      const encryptedValue = await this.encryptData(value);
      await AsyncStorage.setItem(key, encryptedValue);
    } else {
      await AsyncStorage.setItem(key, value);
    }
  }

  async secureRetrieve(key: string): Promise<string | null> {
    const value = await AsyncStorage.getItem(key);
    if (!value) return null;

    if (this.config.enableEncryption) {
      return await this.decryptData(value);
    } else {
      return value;
    }
  }

  // Security audit
  async generateSecurityReport(): Promise<string> {
    const metrics = this.getSecurityMetrics();
    const recentEvents = this.events.slice(-10);

    let report = 'Security Report\n';
    report += '===============\n\n';

    report += `Configuration:\n`;
    report += `  Encryption Enabled: ${this.config.enableEncryption}\n`;
    report += `  Biometrics Enabled: ${this.config.enableBiometrics}\n`;
    report += `  Pin Code Enabled: ${this.config.enablePinCode}\n`;
    report += `  Session Timeout: ${this.config.sessionTimeout} minutes\n`;
    report += `  Max Login Attempts: ${this.config.maxLoginAttempts}\n\n`;

    report += `Metrics:\n`;
    report += `  Total Logins: ${metrics.totalLogins}\n`;
    report += `  Failed Logins: ${metrics.failedLogins}\n`;
    report += `  Security Alerts: ${metrics.securityAlerts}\n`;
    report += `  Last Login: ${metrics.lastLoginTime ? new Date(metrics.lastLoginTime).toLocaleString() : 'Never'}\n\n`;

    report += `Recent Events:\n`;
    for (const event of recentEvents) {
      report += `  ${new Date(event.timestamp).toLocaleString()} - ${event.type}${event.userId ? ` (${event.userId})` : ''}\n`;
    }

    return report;
  }

  // Cleanup
  async cleanup(): Promise<void> {
    // Clear old events (older than 30 days)
    const thirtyDaysAgo = Date.now() - (30 * 24 * 60 * 60 * 1000);
    this.events = this.events.filter(event => event.timestamp > thirtyDaysAgo);
    await AsyncStorage.setItem('security_events', JSON.stringify(this.events));
  }
}

export const securityManager = SecurityManager.getInstance();

// Convenience functions
export const validatePassword = (password: string): { isValid: boolean; errors: string[] } => {
  return securityManager.validatePassword(password);
};

export const trackLoginAttempt = async (userId: string, success: boolean): Promise<void> => {
  return securityManager.trackLoginAttempt(userId, success);
};

export const isAccountLocked = (userId: string): boolean => {
  return securityManager.isAccountLocked(userId);
};

export const startSession = (userId: string): void => {
  return securityManager.startSession(userId);
};

export const isSessionValid = (userId: string): boolean => {
  return securityManager.isSessionValid(userId);
};

export const endSession = (userId: string): void => {
  return securityManager.endSession(userId);
}; 