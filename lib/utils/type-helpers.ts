// Type utilities for common patterns
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>;

export type OptionalFields<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

export type AsyncReturnType<T extends (...args: any[]) => Promise<any>> = 
  T extends (...args: any[]) => Promise<infer R> ? R : never;

export type ComponentProps<T> = T extends React.ComponentType<infer P> ? P : never;

// Strict event handlers
export type EventHandler<T = Event> = (event: T) => void | Promise<void>;

// API response types
export type ApiResponse<T = unknown> = {
  data: T;
  success: boolean;
  message?: string;
  error?: string;
};

// Pagination types
export type PaginationParams = {
  page: number;
  limit: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
};

export type PaginatedResponse<T> = {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
}; 