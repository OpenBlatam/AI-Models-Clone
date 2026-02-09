// API Types

export interface ApiRequestConfig {
  method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  url: string;
  data?: unknown;
  params?: Record<string, unknown>;
  headers?: Record<string, string>;
  timeout?: number;
  signal?: AbortSignal;
}

export interface ApiResponse<T = unknown> {
  data: T;
  status: number;
  statusText: string;
  headers: Record<string, string>;
  config: ApiRequestConfig;
}

export interface ApiError {
  message: string;
  status: number;
  statusText?: string;
  errors?: Record<string, string[]>;
  data?: unknown;
  config?: ApiRequestConfig;
}

export interface PaginatedResponse<T> {
  data: T[];
  page: number;
  limit: number;
  total: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
}

export interface ApiRequestOptions {
  retry?: number;
  retryDelay?: number;
  timeout?: number;
  cache?: boolean;
  cacheTTL?: number;
}

export interface ApiInterceptor {
  request?: (config: ApiRequestConfig) => ApiRequestConfig | Promise<ApiRequestConfig>;
  response?: (response: ApiResponse) => ApiResponse | Promise<ApiResponse>;
  error?: (error: ApiError) => ApiError | Promise<ApiError>;
}

export interface ApiClientConfig {
  baseURL: string;
  timeout?: number;
  headers?: Record<string, string>;
  interceptors?: ApiInterceptor[];
}

export interface QueryParams {
  page?: number;
  limit?: number;
  sort?: string;
  order?: 'asc' | 'desc';
  search?: string;
  filter?: Record<string, unknown>;
}

export interface MutationOptions<TData = unknown, TVariables = unknown> {
  onSuccess?: (data: TData, variables: TVariables) => void;
  onError?: (error: ApiError, variables: TVariables) => void;
  onSettled?: (data: TData | undefined, error: ApiError | null, variables: TVariables) => void;
}

export interface QueryOptions<TData = unknown> {
  enabled?: boolean;
  staleTime?: number;
  cacheTime?: number;
  refetchOnMount?: boolean;
  refetchOnWindowFocus?: boolean;
  refetchInterval?: number;
  onSuccess?: (data: TData) => void;
  onError?: (error: ApiError) => void;
}

