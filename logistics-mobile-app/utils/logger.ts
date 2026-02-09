import { IS_DEV } from '@/constants/config';

// Logging Utilities

type LogLevel = 'debug' | 'info' | 'warn' | 'error';

interface LogEntry {
  level: LogLevel;
  message: string;
  data?: unknown;
  timestamp: string;
}

class Logger {
  private logs: LogEntry[] = [];
  private maxLogs = 100;

  private formatMessage(level: LogLevel, message: string, data?: unknown): string {
    const timestamp = new Date().toISOString();
    const prefix = `[${timestamp}] [${level.toUpperCase()}]`;
    
    if (data) {
      return `${prefix} ${message}\n${JSON.stringify(data, null, 2)}`;
    }
    
    return `${prefix} ${message}`;
  }

  private addLog(level: LogLevel, message: string, data?: unknown): void {
    const entry: LogEntry = {
      level,
      message,
      data,
      timestamp: new Date().toISOString(),
    };

    this.logs.push(entry);
    
    // Keep only last maxLogs entries
    if (this.logs.length > this.maxLogs) {
      this.logs.shift();
    }
  }

  debug(message: string, data?: unknown): void {
    this.addLog('debug', message, data);
    if (IS_DEV) {
      console.debug(this.formatMessage('debug', message, data));
    }
  }

  info(message: string, data?: unknown): void {
    this.addLog('info', message, data);
    if (IS_DEV) {
      console.info(this.formatMessage('info', message, data));
    }
  }

  warn(message: string, data?: unknown): void {
    this.addLog('warn', message, data);
    if (IS_DEV) {
      console.warn(this.formatMessage('warn', message, data));
    }
  }

  error(message: string, error?: Error | unknown): void {
    const errorData = error instanceof Error 
      ? { message: error.message, stack: error.stack }
      : error;
    
    this.addLog('error', message, errorData);
    console.error(this.formatMessage('error', message, errorData));
  }

  getLogs(level?: LogLevel): LogEntry[] {
    if (level) {
      return this.logs.filter((log) => log.level === level);
    }
    return [...this.logs];
  }

  clearLogs(): void {
    this.logs = [];
  }

  exportLogs(): string {
    return JSON.stringify(this.logs, null, 2);
  }
}

export const logger = new Logger();

// Convenience functions
export function logDebug(message: string, data?: unknown): void {
  logger.debug(message, data);
}

export function logInfo(message: string, data?: unknown): void {
  logger.info(message, data);
}

export function logWarn(message: string, data?: unknown): void {
  logger.warn(message, data);
}

export function logError(message: string, error?: Error | unknown): void {
  logger.error(message, error);
}

