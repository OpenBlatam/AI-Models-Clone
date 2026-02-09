import { getApiUrl } from '@/constants/config';
import { getApiKey } from './storage';
import { logger } from './logger';

interface RequestOptions extends RequestInit {
  timeout?: number;
}

class ApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    public data?: unknown,
    message?: string
  ) {
    super(message || `API Error: ${status} ${statusText}`);
    this.name = 'ApiError';
  }
}

async function fetchWithTimeout(
  url: string,
  options: RequestOptions = {},
  timeout = 30000
): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    if (error instanceof Error && error.name === 'AbortError') {
      throw new ApiError(408, 'Request Timeout', undefined, 'Request timed out');
    }
    throw error;
  }
}

export async function apiClient<T>(
  path: string,
  options: RequestOptions = {}
): Promise<T> {
  const url = getApiUrl(path);
  const apiKey = await getApiKey();

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (apiKey) {
    headers['Authorization'] = `Bearer ${apiKey}`;
  }

  try {
    const response = await fetchWithTimeout(
      url,
      {
        ...options,
        headers,
      },
      options.timeout
    );

    const contentType = response.headers.get('content-type');
    const isJson = contentType?.includes('application/json');
    const data = isJson ? await response.json() : await response.text();

    if (!response.ok) {
      const errorMessage =
        typeof data === 'object' && data !== null && 'detail' in data
          ? String(data.detail)
          : undefined;
      
      logger.error(`API Error: ${response.status} ${response.statusText}`, undefined, { url, data });
      
      throw new ApiError(
        response.status,
        response.statusText,
        data,
        errorMessage
      );
    }

    logger.debug(`API Success: ${options.method || 'GET'} ${url}`);
    return data as T;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }

    if (error instanceof Error) {
      logger.error(`Network Error: ${error.message}`, error, { url });
      throw new ApiError(0, 'Network Error', undefined, error.message);
    }

    logger.error('Unknown API Error', undefined, { url });
    throw new ApiError(500, 'Unknown Error', undefined, 'An unknown error occurred');
  }
}

export async function get<T>(path: string, options?: RequestOptions): Promise<T> {
  return apiClient<T>(path, { ...options, method: 'GET' });
}

export async function post<T>(path: string, body?: unknown, options?: RequestOptions): Promise<T> {
  return apiClient<T>(path, {
    ...options,
    method: 'POST',
    body: body ? JSON.stringify(body) : undefined,
  });
}

export async function put<T>(path: string, body?: unknown, options?: RequestOptions): Promise<T> {
  return apiClient<T>(path, {
    ...options,
    method: 'PUT',
    body: body ? JSON.stringify(body) : undefined,
  });
}

export async function del<T>(path: string, options?: RequestOptions): Promise<T> {
  return apiClient<T>(path, { ...options, method: 'DELETE' });
}

export { ApiError };

