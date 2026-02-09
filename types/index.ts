// Base types for the application
export interface BaseEntity {
  id: string;
  createdAt: Date;
  updatedAt: Date;
}

// User related types
export interface User extends BaseEntity {
  email: string;
  name: string;
  avatar?: string;
  role: UserRole;
  isActive: boolean;
  preferences: UserPreferences;
}

export type UserRole = 'admin' | 'user' | 'moderator' | 'premium';

export interface UserPreferences {
  theme: 'light' | 'dark' | 'system';
  language: string;
  notifications: NotificationSettings;
  privacy: PrivacySettings;
}

export interface NotificationSettings {
  email: boolean;
  push: boolean;
  sms: boolean;
  marketing: boolean;
}

export interface PrivacySettings {
  profileVisibility: 'public' | 'private' | 'friends';
  dataSharing: boolean;
  analytics: boolean;
}

// API response types
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  timestamp: Date;
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
}

// Form types
export interface FormField {
  name: string;
  label: string;
  type: 'text' | 'email' | 'password' | 'number' | 'select' | 'textarea' | 'checkbox' | 'radio';
  required: boolean;
  placeholder?: string;
  options?: Array<{ value: string; label: string }>;
  validation?: ValidationRule[];
}

export interface ValidationRule {
  type: 'required' | 'minLength' | 'maxLength' | 'pattern' | 'custom';
  value?: any;
  message: string;
}

// Component props types
export interface BaseComponentProps {
  className?: string;
  children?: any;
  id?: string;
  'data-testid'?: string;
}

export interface ButtonProps extends BaseComponentProps {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'destructive';
  size?: 'sm' | 'md' | 'lg' | 'xl';
  disabled?: boolean;
  loading?: boolean;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
}

export interface InputProps extends BaseComponentProps {
  type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url';
  placeholder?: string;
  value?: string;
  onChange?: (value: string) => void;
  onBlur?: () => void;
  onFocus?: () => void;
  disabled?: boolean;
  required?: boolean;
  error?: string;
  label?: string;
  helperText?: string;
}

// Modal types
export interface ModalProps extends BaseComponentProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  closeOnOverlayClick?: boolean;
  closeOnEscape?: boolean;
}

// Toast notification types
export interface ToastProps {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
}

// Theme types
export interface Theme {
  name: string;
  colors: {
    primary: string;
    secondary: string;
    accent: string;
    background: string;
    surface: string;
    text: string;
    textSecondary: string;
    border: string;
    error: string;
    warning: string;
    success: string;
    info: string;
  };
  spacing: {
    xs: string;
    sm: string;
    md: string;
    lg: string;
    xl: string;
    xxl: string;
  };
  borderRadius: {
    sm: string;
    md: string;
    lg: string;
    xl: string;
  };
  shadows: {
    sm: string;
    md: string;
    lg: string;
    xl: string;
  };
}

// Performance monitoring types
export interface PerformanceMetrics {
  pageLoadTime: number;
  timeToFirstByte: number;
  timeToInteractive: number;
  firstContentfulPaint: number;
  largestContentfulPaint: number;
  cumulativeLayoutShift: number;
  firstInputDelay: number;
}

export interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
  errorInfo?: any;
}

// Animation types
export interface AnimationConfig {
  duration: number;
  easing: string;
  delay?: number;
  stagger?: number;
}

export interface MotionVariants {
  initial: any;
  animate: any;
  exit: any;
  hover?: any;
  tap?: any;
  focus?: any;
}

// API error types
export interface ApiError {
  code: string;
  message: string;
  details?: any;
  timestamp: Date;
  path: string;
  method: string;
}

// Search and filter types
export interface SearchFilters {
  query?: string;
  category?: string;
  tags?: string[];
  dateRange?: {
    start: Date;
    end: Date;
  };
  priceRange?: {
    min: number;
    max: number;
  };
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

// File upload types
export interface FileUpload {
  id: string;
  name: string;
  size: number;
  type: string;
  url: string;
  progress: number;
  status: 'uploading' | 'completed' | 'error';
  error?: string;
}

// Chart data types
export interface ChartDataPoint {
  label: string;
  value: number;
  color?: string;
}

export interface ChartConfig {
  type: 'line' | 'bar' | 'pie' | 'doughnut' | 'radar';
  data: ChartDataPoint[];
  options?: any;
}

// Real-time types
export interface RealtimeEvent {
  id: string;
  type: string;
  data: any;
  timestamp: Date;
  userId?: string;
}

// Web3 types
export interface WalletConnection {
  address: string;
  chainId: number;
  isConnected: boolean;
  balance: string;
  network: string;
}

// Internationalization types
export interface LocaleConfig {
  code: string;
  name: string;
  flag: string;
  direction: 'ltr' | 'rtl';
}

export interface TranslationNamespace {
  [key: string]: string | TranslationNamespace;
}

// Testing types
export interface TestConfig {
  environment: 'test' | 'staging' | 'production';
  timeout: number;
  retries: number;
  parallel: boolean;
}

// Utility types
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>;

export type OptionalFields<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

export type ValueOf<T> = T[keyof T];

export type AsyncReturnType<T extends (...args: any) => Promise<any>> = Awaited<ReturnType<T>>;

// Event types
export interface AppEvent<T = any> {
  type: string;
  payload: T;
  timestamp: Date;
  userId?: string;
  sessionId?: string;
}

// Cache types
export interface CacheEntry<T = any> {
  key: string;
  value: T;
  timestamp: Date;
  ttl: number;
  isExpired: boolean;
}

// Logger types
export interface LogLevel {
  DEBUG: 0;
  INFO: 1;
  WARN: 2;
  ERROR: 3;
  FATAL: 4;
}

export interface LogEntry {
  level: keyof LogLevel;
  message: string;
  timestamp: Date;
  context?: any;
  userId?: string;
  sessionId?: string;
  trace?: string;
}
