// Hook Types

import { DependencyList } from 'react';

export interface UseAsyncOptions<T> {
  immediate?: boolean;
  onSuccess?: (data: T) => void;
  onError?: (error: Error) => void;
}

export interface UseAsyncReturn<T> {
  data: T | null;
  error: Error | null;
  isLoading: boolean;
  execute: (...args: unknown[]) => Promise<T>;
  reset: () => void;
}

export interface UseDebounceOptions {
  delay?: number;
  leading?: boolean;
  trailing?: boolean;
}

export interface UseThrottleOptions {
  leading?: boolean;
  trailing?: boolean;
}

export interface UseIntervalOptions {
  immediate?: boolean;
  delay: number | null;
}

export interface UsePreviousReturn<T> {
  previous: T | undefined;
  current: T;
}

export interface UseToggleReturn {
  value: boolean;
  toggle: () => void;
  setTrue: () => void;
  setFalse: () => void;
}

export interface UseCounterReturn {
  count: number;
  increment: () => void;
  decrement: () => void;
  reset: () => void;
  setCount: (count: number) => void;
}

export interface UseLocalStorageReturn<T> {
  storedValue: T;
  setValue: (value: T | ((val: T) => T)) => Promise<void>;
  removeValue: () => Promise<void>;
  isLoading: boolean;
  error: Error | null;
}

export interface UseMediaQueryReturn {
  isSm: boolean;
  isMd: boolean;
  isLg: boolean;
  isXl: boolean;
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  width: number;
}

export interface UseWindowDimensionsReturn {
  width: number;
  height: number;
  scale: number;
  fontScale: number;
}

export interface UseKeyboardReturn {
  isVisible: boolean;
  height: number;
  dismiss: () => void;
}

export interface UseNetworkStatusReturn {
  isConnected: boolean | null;
  isInternetReachable: boolean | null;
  type: string;
}

export interface UsePermissionsReturn {
  granted: boolean;
  canAskAgain: boolean;
  status: string;
  isLoading: boolean;
  requestPermission: () => Promise<boolean>;
}

export interface UseLocationReturn {
  location: {
    latitude: number;
    longitude: number;
    accuracy?: number;
    altitude?: number | null;
    heading?: number | null;
    speed?: number | null;
  } | null;
  error: string | null;
  isLoading: boolean;
  refreshLocation: () => Promise<void>;
  hasPermission: boolean;
}

export interface UseImagePickerReturn {
  image: {
    uri: string;
    width: number;
    height: number;
    type?: string;
    fileName?: string;
  } | null;
  isLoading: boolean;
  error: string | null;
  pickImage: (source: 'camera' | 'library') => Promise<void>;
  clearImage: () => void;
  hasPermission: boolean;
}

export interface UseClipboardReturn {
  clipboardContent: string;
  isLoading: boolean;
  copyToClipboard: (text: string) => Promise<boolean>;
  readClipboard: () => Promise<string>;
}

export interface UseAppStateReturn {
  appState: 'active' | 'background' | 'inactive';
  isActive: boolean;
  isBackground: boolean;
  isInactive: boolean;
}

export interface UseFocusEffectOptions {
  dependencies?: DependencyList;
}

export interface UseHapticFeedbackReturn {
  light: () => void;
  medium: () => void;
  heavy: () => void;
  success: () => void;
  warning: () => void;
  error: () => void;
  selection: () => void;
}

