import * as ErrorReporter from 'expo-error-reporter';
import { logger } from './logger';

// Configure error reporter
ErrorReporter.setOptions({
  enableInExpoDevelopment: false,
  enableInProduction: true,
});

export function reportError(error: Error, context?: Record<string, unknown>) {
  logger.error('Error reported', error, context);
  
  // In production, send to error tracking service
  if (!__DEV__) {
    ErrorReporter.report(error, {
      ...context,
      timestamp: new Date().toISOString(),
    });
  }
}

export function setUserContext(userId: string, userEmail?: string) {
  ErrorReporter.setUserContext({
    id: userId,
    email: userEmail,
  });
}

export function clearUserContext() {
  ErrorReporter.clearUserContext();
}


