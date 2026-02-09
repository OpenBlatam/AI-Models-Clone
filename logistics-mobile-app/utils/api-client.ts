import axios, { AxiosInstance, AxiosError, AxiosRequestConfig } from 'axios';
import * as SecureStore from 'expo-secure-store';
import { API_URL, API_TIMEOUT } from './config';
import { ApiError } from '@/types';
import { formatErrorMessage } from './error-handler';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      timeout: API_TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    // Request interceptor for auth token
    this.client.interceptors.request.use(
      async (config) => {
        const token = await SecureStore.getItemAsync('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        let message = 'An error occurred';
        let status = 500;
        let errors: Record<string, string[]> | undefined;

        if (error.response) {
          // Server responded with error status
          status = error.response.status;
          const data = error.response.data as any;

          if (data?.message) {
            message = data.message;
          } else if (data?.detail) {
            message = data.detail;
          } else if (typeof data === 'string') {
            message = data;
          }

          if (data?.errors) {
            errors = data.errors;
          }
        } else if (error.request) {
          // Request made but no response received
          message = 'Network error. Please check your connection.';
          status = 0;
        } else {
          // Error setting up request
          message = error.message || 'An error occurred';
        }

        const apiError: ApiError = {
          message: formatErrorMessage({ message, status, errors }),
          status,
          errors,
        };

        return Promise.reject(apiError);
      }
    );
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.get<T>(url, config);
    return response.data;
  }

  async post<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.post<T>(url, data, config);
    return response.data;
  }

  async patch<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.patch<T>(url, data, config);
    return response.data;
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.delete<T>(url, config);
    return response.data;
  }

  async put<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.put<T>(url, data, config);
    return response.data;
  }

  // For file uploads
  async upload<T>(url: string, formData: FormData, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.post<T>(url, formData, {
      ...config,
      headers: {
        'Content-Type': 'multipart/form-data',
        ...config?.headers,
      },
    });
    return response.data;
  }
}

export const apiClient = new ApiClient();

