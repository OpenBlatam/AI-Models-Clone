// Common API response types
export interface ApiResponse<T = any> {
  data: T;
  message: string;
  success: boolean;
  error?: string;
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

// User types
export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  role: UserRole;
  createdAt: Date;
  updatedAt: Date;
}

export type UserRole = 'user' | 'admin' | 'moderator';

// Form types
export interface FormField {
  name: string;
  label: string;
  type: 'text' | 'email' | 'password' | 'number' | 'textarea' | 'select';
  placeholder?: string;
  required?: boolean;
  validation?: ValidationRule[];
  options?: SelectOption[];
}

export interface ValidationRule {
  type: 'required' | 'minLength' | 'maxLength' | 'pattern' | 'custom';
  value?: any;
  message: string;
}

export interface SelectOption {
  value: string | number;
  label: string;
}

// Component props types
export interface BaseComponentProps {
  className?: string;
  children?: React.ReactNode;
}

export interface LoadingState {
  isLoading: boolean;
  error?: string | null;
}

// Theme types
export type Theme = 'light' | 'dark' | 'system';

// Navigation types
export interface NavigationItem {
  label: string;
  href: string;
  icon?: React.ComponentType<{ className?: string }>;
  children?: NavigationItem[];
  external?: boolean;
}

// Toast types
export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface Toast {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
  duration?: number;
}

// API Error types
export interface ApiError {
  status: number;
  message: string;
  code?: string;
  details?: Record<string, any>;
}

// Search and filter types
export interface SearchParams {
  query?: string;
  page?: number;
  limit?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
  filters?: Record<string, any>;
}

// File upload types
export interface FileUpload {
  id: string;
  name: string;
  size: number;
  type: string;
  url: string;
  uploadedAt: Date;
}

// Notification types
export interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  read: boolean;
  createdAt: Date;
  actionUrl?: string;
}

// Settings types
export interface UserSettings {
  theme: Theme;
  language: string;
  notifications: {
    email: boolean;
    push: boolean;
    sms: boolean;
  };
  privacy: {
    profileVisibility: 'public' | 'private' | 'friends';
    showEmail: boolean;
    showLocation: boolean;
  };
}

// Event types
export interface AppEvent {
  id: string;
  name: string;
  description: string;
  startDate: Date;
  endDate: Date;
  location?: string;
  attendees: User[];
  maxAttendees?: number;
  category: string;
  tags: string[];
}

// Utility types
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

export type RequireFields<T, K extends keyof T> = T & Required<Pick<T, K>>;

// Component state types
export interface AsyncState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export interface FormState<T> {
  values: T;
  errors: Partial<Record<keyof T, string>>;
  touched: Partial<Record<keyof T, boolean>>;
  isValid: boolean;
  isSubmitting: boolean;
}





