// Storage Types

export interface StorageItem<T = unknown> {
  key: string;
  value: T;
  timestamp: number;
  ttl?: number;
}

export interface StorageOptions {
  ttl?: number;
  encrypt?: boolean;
}

export interface StorageAdapter {
  getItem: <T>(key: string) => Promise<T | null>;
  setItem: <T>(key: string, value: T, options?: StorageOptions) => Promise<boolean>;
  removeItem: (key: string) => Promise<boolean>;
  clear: () => Promise<boolean>;
  getAllKeys: () => Promise<string[]>;
}

export interface CacheEntry<T> {
  data: T;
  timestamp: number;
  ttl: number;
  isStale: boolean;
}

export interface CacheOptions {
  ttl?: number;
  maxSize?: number;
  strategy?: 'lru' | 'fifo' | 'lfu';
}

export interface CacheAdapter<T> {
  get: (key: string) => Promise<CacheEntry<T> | null>;
  set: (key: string, value: T, options?: CacheOptions) => Promise<void>;
  delete: (key: string) => Promise<void>;
  clear: () => Promise<void>;
  has: (key: string) => Promise<boolean>;
  size: () => Promise<number>;
}

