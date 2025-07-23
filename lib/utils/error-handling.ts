// Error handling utilities with TypeScript

export class AppError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode: number = 500,
    public isOperational: boolean = true
  ) {
    super(message);
    this.name = 'AppError';
  }
}

export class ValidationError extends AppError {
  constructor(message: string, public field?: string) {
    super(message, 'VALIDATION_ERROR', 400);
    this.name = 'ValidationError';
  }
}

export class NotFoundError extends AppError {
  constructor(resource: string) {
    super(`${resource} not found`, 'NOT_FOUND', 404);
    this.name = 'NotFoundError';
  }
}

export class UnauthorizedError extends AppError {
  constructor(message: string = 'Unauthorized') {
    super(message, 'UNAUTHORIZED', 401);
    this.name = 'UnauthorizedError';
  }
}

// Error handler with type safety
export const handleError = (error: unknown): AppError => {
  if (error instanceof AppError) {
    return error;
  }
  
  if (error instanceof Error) {
    return new AppError(error.message, 'UNKNOWN_ERROR');
  }
  
  return new AppError('An unknown error occurred', 'UNKNOWN_ERROR');
};

// Async error wrapper
export const withErrorHandling = <T extends any[], R>(
  fn: (...args: T) => Promise<R>
) => {
  return async (...args: T): Promise<R> => {
    try {
      return await fn(...args);
    } catch (error) {
      throw handleError(error);
    }
  };
};

// Result type for error handling
export type Result<T, E = AppError> = 
  | { success: true; data: T }
  | { success: false; error: E };

export const createResult = {
  success: <T>(data: T): Result<T> => ({ success: true, data }),
  error: <E>(error: E): Result<never, E> => ({ success: false, error }),
};

// Safe async execution
export const safeAsync = async <T>(
  fn: () => Promise<T>
): Promise<Result<T>> => {
  try {
    const data = await fn();
    return createResult.success(data);
  } catch (error) {
    return createResult.error(handleError(error));
  }
}; 