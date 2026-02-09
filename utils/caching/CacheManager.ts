import AsyncStorage from '@react-native-async-storage/async-storage';

export interface CacheConfig {
  maxSize: number; // MB
  maxAge: number; // milliseconds
  enableCompression: boolean;
  enableEncryption: boolean;
  cleanupInterval: number; // milliseconds
}

export interface CacheEntry<T = any> {
  key: string;
  value: T;
  timestamp: number;
  size: number;
  accessCount: number;
  lastAccessed: number;
}

export interface CacheStats {
  totalEntries: number;
  totalSize: number; // bytes
  hitRate: number;
  missRate: number;
  averageAccessTime: number;
  oldestEntry: number;
  newestEntry: number;
}

export type CacheStrategy = 'lru' | 'lfu' | 'fifo' | 'ttl';

class CacheManager {
  private static instance: CacheManager;
  private config: CacheConfig;
  private cache: Map<string, CacheEntry> = new Map();
  private stats = {
    hits: 0,
    misses: 0,
    totalAccessTime: 0,
    accessCount: 0,
  };
  private isInitialized: boolean = false;

  private constructor() {
    this.config = {
      maxSize: 50, // 50MB
      maxAge: 24 * 60 * 60 * 1000, // 24 hours
      enableCompression: true,
      enableEncryption: false,
      cleanupInterval: 60 * 60 * 1000, // 1 hour
    };
  }

  static getInstance(): CacheManager {
    if (!CacheManager.instance) {
      CacheManager.instance = new CacheManager();
    }
    return CacheManager.instance;
  }

  async initialize(): Promise<void> {
    if (this.isInitialized) return;

    try {
      // Load saved configuration
      const savedConfig = await AsyncStorage.getItem('cache_config');
      if (savedConfig) {
        this.config = { ...this.config, ...JSON.parse(savedConfig) };
      }

      // Load cached data
      const cachedData = await AsyncStorage.getItem('cache_data');
      if (cachedData) {
        const entries = JSON.parse(cachedData);
        for (const [key, entry] of Object.entries(entries)) {
          this.cache.set(key, entry as CacheEntry);
        }
      }

      // Start cleanup interval
      this.startCleanupInterval();

      this.isInitialized = true;
    } catch (error) {
      console.error('CacheManager initialization failed:', error);
    }
  }

  // Configuration management
  getConfig(): CacheConfig {
    return { ...this.config };
  }

  async updateConfig(newConfig: Partial<CacheConfig>): Promise<void> {
    this.config = { ...this.config, ...newConfig };
    await AsyncStorage.setItem('cache_config', JSON.stringify(this.config));
  }

  // Cache operations
  async set<T>(key: string, value: T, options?: { ttl?: number; strategy?: CacheStrategy }): Promise<void> {
    const startTime = performance.now();
    const timestamp = Date.now();
    const size = this.calculateSize(value);

    // Check if we need to evict entries
    await this.ensureCapacity(size);

    const entry: CacheEntry<T> = {
      key,
      value,
      timestamp,
      size,
      accessCount: 0,
      lastAccessed: timestamp,
    };

    this.cache.set(key, entry);
    await this.persistCache();

    const accessTime = performance.now() - startTime;
    this.updateStats(accessTime, false);
  }

  async get<T>(key: string): Promise<T | null> {
    const startTime = performance.now();
    const entry = this.cache.get(key);

    if (!entry) {
      this.updateStats(performance.now() - startTime, false);
      return null;
    }

    // Check if entry has expired
    if (this.isExpired(entry)) {
      this.cache.delete(key);
      await this.persistCache();
      this.updateStats(performance.now() - startTime, false);
      return null;
    }

    // Update access statistics
    entry.accessCount++;
    entry.lastAccessed = Date.now();
    this.cache.set(key, entry);
    await this.persistCache();

    const accessTime = performance.now() - startTime;
    this.updateStats(accessTime, true);

    return entry.value as T;
  }

  async has(key: string): Promise<boolean> {
    const entry = this.cache.get(key);
    if (!entry) return false;

    if (this.isExpired(entry)) {
      this.cache.delete(key);
      await this.persistCache();
      return false;
    }

    return true;
  }

  async delete(key: string): Promise<boolean> {
    const deleted = this.cache.delete(key);
    if (deleted) {
      await this.persistCache();
    }
    return deleted;
  }

  async clear(): Promise<void> {
    this.cache.clear();
    await this.persistCache();
  }

  // Cache strategies
  private async ensureCapacity(newEntrySize: number): Promise<void> {
    const currentSize = this.getTotalSize();
    const maxSizeBytes = this.config.maxSize * 1024 * 1024;

    if (currentSize + newEntrySize <= maxSizeBytes) {
      return;
    }

    // Sort entries by strategy (LRU by default)
    const entries = Array.from(this.cache.entries());
    entries.sort((a, b) => a[1].lastAccessed - b[1].lastAccessed);

    // Remove entries until we have enough space
    for (const [key, entry] of entries) {
      this.cache.delete(key);
      const newSize = this.getTotalSize() + newEntrySize;
      if (newSize <= maxSizeBytes) {
        break;
      }
    }
  }

  private isExpired(entry: CacheEntry): boolean {
    const now = Date.now();
    return now - entry.timestamp > this.config.maxAge;
  }

  private calculateSize(value: any): number {
    // Rough size calculation
    const serialized = JSON.stringify(value);
    return new Blob([serialized]).size;
  }

  private getTotalSize(): number {
    let totalSize = 0;
    for (const entry of this.cache.values()) {
      totalSize += entry.size;
    }
    return totalSize;
  }

  private updateStats(accessTime: number, isHit: boolean): void {
    this.stats.accessCount++;
    this.stats.totalAccessTime += accessTime;

    if (isHit) {
      this.stats.hits++;
    } else {
      this.stats.misses++;
    }
  }

  // Statistics
  getStats(): CacheStats {
    const totalEntries = this.cache.size;
    const totalSize = this.getTotalSize();
    const totalRequests = this.stats.hits + this.stats.misses;
    const hitRate = totalRequests > 0 ? this.stats.hits / totalRequests : 0;
    const missRate = totalRequests > 0 ? this.stats.misses / totalRequests : 0;
    const averageAccessTime = this.stats.accessCount > 0 ? this.stats.totalAccessTime / this.stats.accessCount : 0;

    const timestamps = Array.from(this.cache.values()).map(entry => entry.timestamp);
    const oldestEntry = timestamps.length > 0 ? Math.min(...timestamps) : 0;
    const newestEntry = timestamps.length > 0 ? Math.max(...timestamps) : 0;

    return {
      totalEntries,
      totalSize,
      hitRate,
      missRate,
      averageAccessTime,
      oldestEntry,
      newestEntry,
    };
  }

  // Cache utilities
  async getKeys(): Promise<string[]> {
    return Array.from(this.cache.keys());
  }

  async getSize(): Promise<number> {
    return this.cache.size;
  }

  async getMemoryUsage(): Promise<number> {
    return this.getTotalSize();
  }

  // Persistence
  private async persistCache(): Promise<void> {
    try {
      const cacheData: Record<string, CacheEntry> = {};
      for (const [key, entry] of this.cache.entries()) {
        cacheData[key] = entry;
      }
      await AsyncStorage.setItem('cache_data', JSON.stringify(cacheData));
    } catch (error) {
      console.error('Failed to persist cache:', error);
    }
  }

  // Cleanup
  private startCleanupInterval(): void {
    setInterval(() => {
      this.cleanup();
    }, this.config.cleanupInterval);
  }

  private async cleanup(): Promise<void> {
    const now = Date.now();
    const expiredKeys: string[] = [];

    for (const [key, entry] of this.cache.entries()) {
      if (this.isExpired(entry)) {
        expiredKeys.push(key);
      }
    }

    for (const key of expiredKeys) {
      this.cache.delete(key);
    }

    if (expiredKeys.length > 0) {
      await this.persistCache();
      if (__DEV__) {
        console.log(`Cache cleanup: removed ${expiredKeys.length} expired entries`);
      }
    }
  }

  // Cache warming
  async warmCache<T>(entries: Array<{ key: string; value: T }>): Promise<void> {
    for (const entry of entries) {
      await this.set(entry.key, entry.value);
    }
  }

  // Cache prefetching
  async prefetch<T>(key: string, fetchFn: () => Promise<T>): Promise<void> {
    try {
      const value = await fetchFn();
      await this.set(key, value);
    } catch (error) {
      console.error(`Failed to prefetch cache for key: ${key}`, error);
    }
  }

  // Cache invalidation patterns
  async invalidatePattern(pattern: RegExp): Promise<number> {
    const keysToDelete: string[] = [];
    
    for (const key of this.cache.keys()) {
      if (pattern.test(key)) {
        keysToDelete.push(key);
      }
    }

    for (const key of keysToDelete) {
      this.cache.delete(key);
    }

    if (keysToDelete.length > 0) {
      await this.persistCache();
    }

    return keysToDelete.length;
  }

  async invalidateNamespace(namespace: string): Promise<number> {
    return this.invalidatePattern(new RegExp(`^${namespace}:`));
  }

  // Cache analytics
  generateCacheReport(): string {
    const stats = this.getStats();
    const entries = Array.from(this.cache.entries());

    let report = 'Cache Report\n';
    report += '============\n\n';

    report += `Configuration:\n`;
    report += `  Max Size: ${this.config.maxSize}MB\n`;
    report += `  Max Age: ${this.config.maxAge / (1000 * 60 * 60)} hours\n`;
    report += `  Compression: ${this.config.enableCompression ? 'Enabled' : 'Disabled'}\n`;
    report += `  Encryption: ${this.config.enableEncryption ? 'Enabled' : 'Disabled'}\n\n`;

    report += `Statistics:\n`;
    report += `  Total Entries: ${stats.totalEntries}\n`;
    report += `  Total Size: ${(stats.totalSize / (1024 * 1024)).toFixed(2)}MB\n`;
    report += `  Hit Rate: ${(stats.hitRate * 100).toFixed(2)}%\n`;
    report += `  Miss Rate: ${(stats.missRate * 100).toFixed(2)}%\n`;
    report += `  Average Access Time: ${stats.averageAccessTime.toFixed(2)}ms\n\n`;

    report += `Top Accessed Entries:\n`;
    const topEntries = entries
      .sort((a, b) => b[1].accessCount - a[1].accessCount)
      .slice(0, 5);

    for (const [key, entry] of topEntries) {
      report += `  ${key}: ${entry.accessCount} accesses, ${(entry.size / 1024).toFixed(2)}KB\n`;
    }

    return report;
  }
}

export const cacheManager = CacheManager.getInstance();

// Convenience functions
export const cacheSet = async <T>(key: string, value: T, options?: { ttl?: number; strategy?: CacheStrategy }): Promise<void> => {
  return cacheManager.set(key, value, options);
};

export const cacheGet = async <T>(key: string): Promise<T | null> => {
  return cacheManager.get<T>(key);
};

export const cacheHas = async (key: string): Promise<boolean> => {
  return cacheManager.has(key);
};

export const cacheDelete = async (key: string): Promise<boolean> => {
  return cacheManager.delete(key);
};

export const cacheClear = async (): Promise<void> => {
  return cacheManager.clear();
};

export const cacheStats = (): CacheStats => {
  return cacheManager.getStats();
}; 