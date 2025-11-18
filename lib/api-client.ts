import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import { z } from 'zod';

// Types
export interface ApiConfig {
  baseURL: string;
  timeout: number;
  headers: Record<string, string>;
  withCredentials: boolean;
}

export interface ApiRequestConfig extends AxiosRequestConfig {
  skipAuth?: boolean;
  retryCount?: number;
  maxRetries?: number;
  retryDelay?: number;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data: T;
  message?: string;
  errors?: Record<string, string[]>;
  meta?: {
    page?: number;
    limit?: number;
    total?: number;
    totalPages?: number;
  };
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  meta: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

export class ApiError extends Error {
  public status: number;
  public statusText: string;
  public data: any;
  public isNetworkError: boolean;
  public isTimeoutError: boolean;
  public isAuthError: boolean;

  constructor(
    message: string,
    status: number,
    statusText: string,
    data?: any,
    isNetworkError = false,
    isTimeoutError = false,
    isAuthError = false
  ) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.statusText = statusText;
    this.data = data;
    this.isNetworkError = isNetworkError;
    this.isTimeoutError = isTimeoutError;
    this.isAuthError = isAuthError;
  }
}

// Default configuration
const defaultConfig: ApiConfig = {
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
};

// Request/Response interceptors
class ApiClient {
  private client: AxiosInstance;
  private config: ApiConfig;

  constructor(config: Partial<ApiConfig> = {}) {
    this.config = { ...defaultConfig, ...config };
    this.client = axios.create(this.config);
    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add auth token if available
        if (typeof window !== 'undefined') {
          const token = localStorage.getItem('auth-token');
          if (token && !config.skipAuth) {
            config.headers.Authorization = `Bearer ${token}`;
          }
        }

        // Add request ID for tracking
        config.headers['X-Request-ID'] = this.generateRequestId();

        // Log request in development
        if (process.env.NODE_ENV === 'development') {
          console.log('API Request:', {
            method: config.method?.toUpperCase(),
            url: config.url,
            data: config.data,
            headers: config.headers,
          });
        }

        return config;
      },
      (error) => {
        console.error('Request interceptor error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response: AxiosResponse) => {
        // Log response in development
        if (process.env.NODE_ENV === 'development') {
          console.log('API Response:', {
            status: response.status,
            url: response.config.url,
            data: response.data,
          });
        }

        return response;
      },
      async (error: AxiosError) => {
        const originalRequest = error.config as any;
        
        // Handle retry logic
        if (this.shouldRetry(error, originalRequest)) {
          return this.retryRequest(originalRequest);
        }

        // Transform error to ApiError
        const apiError = this.transformError(error);
        
        // Handle auth errors
        if (apiError.isAuthError) {
          this.handleAuthError();
        }

        return Promise.reject(apiError);
      }
    );
  }

  private generateRequestId(): string {
    return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private shouldRetry(error: AxiosError, config: any): boolean {
    const retryCount = config.retryCount || 0;
    const maxRetries = config.maxRetries || 3;
    
    return (
      retryCount < maxRetries &&
      (error.code === 'ECONNABORTED' || 
       error.response?.status === 429 ||
       error.response?.status >= 500)
    );
  }

  private async retryRequest(config: any): Promise<AxiosResponse> {
    const retryCount = (config.retryCount || 0) + 1;
    const retryDelay = config.retryDelay || 1000;
    
    config.retryCount = retryCount;
    
    // Exponential backoff
    const delay = retryDelay * Math.pow(2, retryCount - 1);
    
    await new Promise(resolve => setTimeout(resolve, delay));
    
    return this.client.request(config);
  }

  private transformError(error: AxiosError): ApiError {
    if (error.code === 'ECONNABORTED') {
      return new ApiError(
        'Request timeout',
        408,
        'Request Timeout',
        error.response?.data,
        false,
        true,
        false
      );
    }

    if (!error.response) {
      return new ApiError(
        'Network error',
        0,
        'Network Error',
        error.message,
        true,
        false,
        false
      );
    }

    const { status, statusText, data } = error.response;
    const isAuthError = status === 401 || status === 403;

    return new ApiError(
      data?.message || statusText || 'API Error',
      status,
      statusText,
      data,
      false,
      false,
      isAuthError
    );
  }

  private handleAuthError() {
    // Clear auth token and redirect to login
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth-token');
      // You can dispatch a logout action here if using state management
      window.location.href = '/auth/login';
    }
  }

  // Generic request method
  async request<T = any>(
    config: ApiRequestConfig,
    schema?: z.ZodSchema<T>
  ): Promise<ApiResponse<T>> {
    try {
      const response = await this.client.request(config);
      
      // Validate response data if schema provided
      if (schema) {
        const validatedData = schema.parse(response.data);
        return validatedData;
      }
      
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  // HTTP methods with type safety
  async get<T = any>(
    url: string,
    config?: ApiRequestConfig,
    schema?: z.ZodSchema<T>
  ): Promise<ApiResponse<T>> {
    return this.request({ ...config, method: 'GET', url }, schema);
  }

  async post<T = any>(
    url: string,
    data?: any,
    config?: ApiRequestConfig,
    schema?: z.ZodSchema<T>
  ): Promise<ApiResponse<T>> {
    return this.request({ ...config, method: 'POST', url, data }, schema);
  }

  async put<T = any>(
    url: string,
    data?: any,
    config?: ApiRequestConfig,
    schema?: z.ZodSchema<T>
  ): Promise<ApiResponse<T>> {
    return this.request({ ...config, method: 'PUT', url, data }, schema);
  }

  async patch<T = any>(
    url: string,
    data?: any,
    config?: ApiRequestConfig,
    schema?: z.ZodSchema<T>
  ): Promise<ApiResponse<T>> {
    return this.request({ ...config, method: 'PATCH', url, data }, schema);
  }

  async delete<T = any>(
    url: string,
    config?: ApiRequestConfig,
    schema?: z.ZodSchema<T>
  ): Promise<ApiResponse<T>> {
    return this.request({ ...config, method: 'DELETE', url }, schema);
  }

  // Utility methods
  setAuthToken(token: string) {
    this.client.defaults.headers.common.Authorization = `Bearer ${token}`;
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth-token', token);
    }
  }

  clearAuthToken() {
    delete this.client.defaults.headers.common.Authorization;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth-token');
    }
  }

  setBaseURL(baseURL: string) {
    this.client.defaults.baseURL = baseURL;
  }

  // Health check
  async healthCheck(): Promise<boolean> {
    try {
      await this.get('/health');
      return true;
    } catch {
      return false;
    }
  }
}

// Create default instance
export const apiClient = new ApiClient();

// Export types and utilities
export type { ApiConfig, ApiRequestConfig, ApiResponse, PaginatedResponse };
export { ApiError };

// Convenience functions
export const api = {
  get: <T>(url: string, config?: ApiRequestConfig, schema?: z.ZodSchema<T>) =>
    apiClient.get<T>(url, config, schema),
  
  post: <T>(url: string, data?: any, config?: ApiRequestConfig, schema?: z.ZodSchema<T>) =>
    apiClient.post<T>(url, data, config, schema),
  
  put: <T>(url: string, data?: any, config?: ApiRequestConfig, schema?: z.ZodSchema<T>) =>
    apiClient.put<T>(url, data, config, schema),
  
  patch: <T>(url: string, data?: any, config?: ApiRequestConfig, schema?: z.ZodSchema<T>) =>
    apiClient.patch<T>(url, data, config, schema),
  
  delete: <T>(url: string, config?: ApiRequestConfig, schema?: z.ZodSchema<T>) =>
    apiClient.delete<T>(url, config, schema),
  
  setAuthToken: (token: string) => apiClient.setAuthToken(token),
  clearAuthToken: () => apiClient.clearAuthToken(),
  healthCheck: () => apiClient.healthCheck(),
};

// Common response schemas
export const baseResponseSchema = z.object({
  success: z.boolean(),
  message: z.string().optional(),
  errors: z.record(z.array(z.string())).optional(),
});

export const paginatedResponseSchema = <T extends z.ZodTypeAny>(itemSchema: T) =>
  baseResponseSchema.extend({
    data: z.array(itemSchema),
    meta: z.object({
      page: z.number(),
      limit: z.number(),
      total: z.number(),
      totalPages: z.number(),
    }),
  });

// Error handling utilities
export const handleApiError = (error: unknown): string => {
  if (error instanceof ApiError) {
    if (error.isNetworkError) return 'Network error. Please check your connection.';
    if (error.isTimeoutError) return 'Request timeout. Please try again.';
    if (error.isAuthError) return 'Authentication failed. Please log in again.';
    return error.message || 'An unexpected error occurred.';
  }
  
  if (error instanceof Error) {
    return error.message;
  }
  
  return 'An unexpected error occurred.';
};

export const isApiError = (error: unknown): error is ApiError => {
  return error instanceof ApiError;
};
