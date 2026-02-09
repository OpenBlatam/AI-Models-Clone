// Debounce and Throttle Utilities

export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null;

  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      timeout = null;
      func(...args);
    };

    if (timeout) {
      clearTimeout(timeout);
    }
    timeout = setTimeout(later, wait);
  };
}

export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean;
  let lastResult: ReturnType<T>;

  return function executedFunction(...args: Parameters<T>): ReturnType<T> {
    if (!inThrottle) {
      lastResult = func(...args);
      inThrottle = true;
      setTimeout(() => {
        inThrottle = false;
      }, limit);
    }
    return lastResult;
  };
}

export function debounceAsync<T extends (...args: any[]) => Promise<any>>(
  func: T,
  wait: number
): (...args: Parameters<T>) => Promise<ReturnType<T>> {
  let timeout: NodeJS.Timeout | null = null;
  let promiseResolve: ((value: ReturnType<T>) => void) | null = null;
  let promiseReject: ((error: unknown) => void) | null = null;

  return function executedFunction(...args: Parameters<T>): Promise<ReturnType<T>> {
    return new Promise((resolve, reject) => {
      if (timeout) {
        clearTimeout(timeout);
        if (promiseReject) {
          promiseReject(new Error('Debounced'));
        }
      }

      promiseResolve = resolve;
      promiseReject = reject;

      timeout = setTimeout(async () => {
        try {
          const result = await func(...args);
          if (promiseResolve) {
            promiseResolve(result);
          }
        } catch (error) {
          if (promiseReject) {
            promiseReject(error);
          }
        } finally {
          timeout = null;
          promiseResolve = null;
          promiseReject = null;
        }
      }, wait);
    });
  };
}

