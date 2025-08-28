import { performanceMonitor } from '../performance/PerformanceMonitor';
import { analytics } from '../analytics/AnalyticsService';

export interface NetworkOptimizationConfig {
  enableRequestBatching: boolean;
  enableRequestCaching: boolean;
  enableRequestPrioritization: boolean;
  enableConnectionPooling: boolean;
  enableCompression: boolean;
  enableRetryLogic: boolean;
  batchSize: number;
  maxConcurrentRequests: number;
  timeout: number; // ms
  retryAttempts: number;
}

export interface NetworkRequest {
  id: string;
  url: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  priority: 'high' | 'medium' | 'low';
  data?: any;
  headers?: Record<string, string>;
  timestamp: number;
  retryCount: number;
}

export interface NetworkMetrics {
  totalRequests: number;
  successfulRequests: number;
  failedRequests: number;
  averageResponseTime: number;
  averageLatency: number;
  throughput: number; // requests per second
  errorRate: number;
  cacheHitRate: number;
}

export interface BatchRequest {
  id: string;
  requests: NetworkRequest[];
  priority: 'high' | 'medium' | 'low';
  timestamp: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
}

class NetworkOptimizer {
  private static instance: NetworkOptimizer;
  private config: NetworkOptimizationConfig;
  private requestQueue: NetworkRequest[] = [];
  private batchQueue: BatchRequest[] = [];
  private connectionPool: Map<string, any> = new Map();
  private metrics: NetworkMetrics;
  private requestHistory: NetworkRequest[] = [];

  private constructor() {
    this.config = {
      enableRequestBatching: true,
      enableRequestCaching: true,
      enableRequestPrioritization: true,
      enableConnectionPooling: true,
      enableCompression: true,
      enableRetryLogic: true,
      batchSize: 10,
      maxConcurrentRequests: 5,
      timeout: 30000, // 30 seconds
      retryAttempts: 3,
    };

    this.metrics = {
      totalRequests: 0,
      successfulRequests: 0,
      failedRequests: 0,
      averageResponseTime: 0,
      averageLatency: 0,
      throughput: 0,
      errorRate: 0,
      cacheHitRate: 0,
    };
  }

  static getInstance(): NetworkOptimizer {
    if (!NetworkOptimizer.instance) {
      NetworkOptimizer.instance = new NetworkOptimizer();
    }
    return NetworkOptimizer.instance;
  }

  // Configuration management
  getConfig(): NetworkOptimizationConfig {
    return { ...this.config };
  }

  updateConfig(newConfig: Partial<NetworkOptimizationConfig>): void {
    this.config = { ...this.config, ...newConfig };
  }

  // Request batching
  async addToBatch(request: NetworkRequest): Promise<void> {
    if (!this.config.enableRequestBatching) {
      await this.executeRequest(request);
      return;
    }

    // Add request to queue
    this.requestQueue.push(request);

    // Check if we should create a new batch
    if (this.shouldCreateBatch()) {
      await this.createAndExecuteBatch();
    }
  }

  private shouldCreateBatch(): boolean {
    return this.requestQueue.length >= this.config.batchSize ||
           this.hasHighPriorityRequests() ||
           this.isBatchTimeoutReached();
  }

  private hasHighPriorityRequests(): boolean {
    return this.requestQueue.some(req => req.priority === 'high');
  }

  private isBatchTimeoutReached(): boolean {
    if (this.requestQueue.length === 0) return false;
    
    const oldestRequest = this.requestQueue[0];
    const timeSinceOldest = Date.now() - oldestRequest.timestamp;
    
    return timeSinceOldest > 5000; // 5 seconds timeout
  }

  private async createAndExecuteBatch(): Promise<void> {
    if (this.requestQueue.length === 0) return;

    // Group requests by priority
    const highPriority = this.requestQueue.filter(req => req.priority === 'high');
    const mediumPriority = this.requestQueue.filter(req => req.priority === 'medium');
    const lowPriority = this.requestQueue.filter(req => req.priority === 'low');

    // Create batches for each priority level
    const batches: BatchRequest[] = [];

    if (highPriority.length > 0) {
      batches.push(this.createBatch(highPriority, 'high'));
    }

    if (mediumPriority.length > 0) {
      batches.push(this.createBatch(mediumPriority, 'medium'));
    }

    if (lowPriority.length > 0) {
      batches.push(this.createBatch(lowPriority, 'low'));
    }

    // Execute batches in priority order
    for (const batch of batches) {
      await this.executeBatch(batch);
    }

    // Clear the queue
    this.requestQueue = [];
  }

  private createBatch(requests: NetworkRequest[], priority: 'high' | 'medium' | 'low'): BatchRequest {
    return {
      id: `batch_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      requests,
      priority,
      timestamp: Date.now(),
      status: 'pending',
    };
  }

  private async executeBatch(batch: BatchRequest): Promise<void> {
    try {
      console.log(`Executing batch ${batch.id} with ${batch.requests.length} requests`);
      
      batch.status = 'processing';

      // Execute requests in parallel
      const promises = batch.requests.map(request => this.executeRequest(request));
      const results = await Promise.allSettled(promises);

      // Update metrics
      results.forEach((result, index) => {
        const request = batch.requests[index];
        this.updateMetrics(request, result.status === 'fulfilled');
      });

      batch.status = 'completed';
      console.log(`Batch ${batch.id} completed successfully`);
    } catch (error) {
      console.error(`Batch ${batch.id} failed:`, error);
      batch.status = 'failed';
    }
  }

  private async executeRequest(request: NetworkRequest): Promise<any> {
    try {
      console.log(`Executing request: ${request.method} ${request.url}`);

      // Simulate network request
      const response = await this.simulateNetworkRequest(request);
      
      // Store in history
      this.requestHistory.push(request);
      
      // Keep only last 1000 requests
      if (this.requestHistory.length > 1000) {
        this.requestHistory.shift();
      }

      return response;
    } catch (error) {
      console.error(`Request failed: ${request.method} ${request.url}`, error);
      
      // Implement retry logic
      if (this.config.enableRetryLogic && request.retryCount < this.config.retryAttempts) {
        return this.retryRequest(request);
      }
      
      throw error;
    }
  }

  private async simulateNetworkRequest(request: NetworkRequest): Promise<any> {
    // Simulate network latency and response
    const latency = Math.random() * 1000 + 100; // 100-1100ms
    await new Promise(resolve => setTimeout(resolve, latency));

    // Simulate success/failure
    const successRate = 0.95; // 95% success rate
    if (Math.random() > successRate) {
      throw new Error('Network request failed');
    }

    return {
      status: 200,
      data: { message: 'Success', timestamp: Date.now() },
      latency,
    };
  }

  private async retryRequest(request: NetworkRequest): Promise<any> {
    request.retryCount++;
    console.log(`Retrying request ${request.id} (attempt ${request.retryCount})`);
    
    // Exponential backoff
    const delay = Math.pow(2, request.retryCount) * 1000;
    await new Promise(resolve => setTimeout(resolve, delay));
    
    return this.executeRequest(request);
  }

  // Request prioritization
  prioritizeRequests(requests: NetworkRequest[]): NetworkRequest[] {
    if (!this.config.enableRequestPrioritization) {
      return requests;
    }

    return requests.sort((a, b) => {
      const priorityOrder = { high: 3, medium: 2, low: 1 };
      const aPriority = priorityOrder[a.priority];
      const bPriority = priorityOrder[b.priority];
      
      if (aPriority !== bPriority) {
        return bPriority - aPriority;
      }
      
      // If same priority, sort by timestamp (FIFO)
      return a.timestamp - b.timestamp;
    });
  }

  // Connection pooling
  async getConnection(url: string): Promise<any> {
    if (!this.config.enableConnectionPooling) {
      return this.createConnection(url);
    }

    const host = this.extractHost(url);
    let connection = this.connectionPool.get(host);

    if (!connection || this.isConnectionExpired(connection)) {
      connection = await this.createConnection(url);
      this.connectionPool.set(host, connection);
    }

    return connection;
  }

  private extractHost(url: string): string {
    try {
      const urlObj = new URL(url);
      return urlObj.host;
    } catch {
      return url;
    }
  }

  private async createConnection(url: string): Promise<any> {
    // Simulate connection creation
    return {
      url,
      createdAt: Date.now(),
      lastUsed: Date.now(),
      isActive: true,
    };
  }

  private isConnectionExpired(connection: any): boolean {
    const maxAge = 300000; // 5 minutes
    return Date.now() - connection.lastUsed > maxAge;
  }

  // Request caching
  async getCachedResponse(request: NetworkRequest): Promise<any | null> {
    if (!this.config.enableRequestCaching) {
      return null;
    }

    // Simulate cache lookup
    const cacheKey = this.generateCacheKey(request);
    const cached = this.getFromCache(cacheKey);
    
    if (cached && !this.isCacheExpired(cached)) {
      this.metrics.cacheHitRate = (this.metrics.cacheHitRate + 1) / 2;
      return cached.data;
    }

    return null;
  }

  private generateCacheKey(request: NetworkRequest): string {
    return `${request.method}_${request.url}_${JSON.stringify(request.data || {})}`;
  }

  private getFromCache(key: string): any {
    // Simulate cache storage
    const cache = new Map<string, any>();
    return cache.get(key);
  }

  private isCacheExpired(cached: any): boolean {
    const maxAge = 300000; // 5 minutes
    return Date.now() - cached.timestamp > maxAge;
  }

  // Compression optimization
  async compressRequest(request: NetworkRequest): Promise<NetworkRequest> {
    if (!this.config.enableCompression) {
      return request;
    }

    // Simulate compression
    const compressedRequest = { ...request };
    
    if (compressedRequest.data) {
      // Simulate data compression
      compressedRequest.headers = {
        ...compressedRequest.headers,
        'Content-Encoding': 'gzip',
        'Content-Length': JSON.stringify(compressedRequest.data).length.toString(),
      };
    }

    return compressedRequest;
  }

  // Metrics tracking
  private updateMetrics(request: NetworkRequest, success: boolean): void {
    this.metrics.totalRequests++;
    
    if (success) {
      this.metrics.successfulRequests++;
    } else {
      this.metrics.failedRequests++;
    }

    // Update error rate
    this.metrics.errorRate = this.metrics.failedRequests / this.metrics.totalRequests;

    // Update throughput (requests per second)
    const timeWindow = 60000; // 1 minute
    const recentRequests = this.requestHistory.filter(
      req => Date.now() - req.timestamp < timeWindow
    );
    this.metrics.throughput = recentRequests.length / 60; // requests per second
  }

  // Get network metrics
  getMetrics(): NetworkMetrics {
    return { ...this.metrics };
  }

  // Get request history
  getRequestHistory(): NetworkRequest[] {
    return [...this.requestHistory];
  }

  // Clear metrics
  clearMetrics(): void {
    this.metrics = {
      totalRequests: 0,
      successfulRequests: 0,
      failedRequests: 0,
      averageResponseTime: 0,
      averageLatency: 0,
      throughput: 0,
      errorRate: 0,
      cacheHitRate: 0,
    };
  }

  // Generate network optimization report
  generateReport(): string {
    let report = 'Network Optimization Report\n';
    report += '==========================\n\n';

    report += `Configuration:\n`;
    report += `  Request Batching: ${this.config.enableRequestBatching ? 'Enabled' : 'Disabled'}\n`;
    report += `  Request Caching: ${this.config.enableRequestCaching ? 'Enabled' : 'Disabled'}\n`;
    report += `  Request Prioritization: ${this.config.enableRequestPrioritization ? 'Enabled' : 'Disabled'}\n`;
    report += `  Connection Pooling: ${this.config.enableConnectionPooling ? 'Enabled' : 'Disabled'}\n`;
    report += `  Compression: ${this.config.enableCompression ? 'Enabled' : 'Disabled'}\n`;
    report += `  Retry Logic: ${this.config.enableRetryLogic ? 'Enabled' : 'Disabled'}\n\n`;

    report += `Performance Metrics:\n`;
    report += `  Total Requests: ${this.metrics.totalRequests}\n`;
    report += `  Successful Requests: ${this.metrics.successfulRequests}\n`;
    report += `  Failed Requests: ${this.metrics.failedRequests}\n`;
    report += `  Error Rate: ${(this.metrics.errorRate * 100).toFixed(2)}%\n`;
    report += `  Throughput: ${this.metrics.throughput.toFixed(2)} req/s\n`;
    report += `  Cache Hit Rate: ${(this.metrics.cacheHitRate * 100).toFixed(2)}%\n\n`;

    report += `Queue Status:\n`;
    report += `  Pending Requests: ${this.requestQueue.length}\n`;
    report += `  Active Batches: ${this.batchQueue.filter(b => b.status === 'processing').length}\n`;
    report += `  Connection Pool Size: ${this.connectionPool.size}\n\n`;

    if (this.requestHistory.length > 0) {
      const recentRequests = this.requestHistory.slice(-10);
      report += `Recent Requests:\n`;
      recentRequests.forEach((req, index) => {
        report += `  ${index + 1}. ${req.method} ${req.url} (${req.priority})\n`;
      });
    }

    return report;
  }
}

export const networkOptimizer = NetworkOptimizer.getInstance();

// Convenience functions
export const addRequestToBatch = async (request: NetworkRequest): Promise<void> => {
  return networkOptimizer.addToBatch(request);
};

export const getNetworkMetrics = (): NetworkMetrics => {
  return networkOptimizer.getMetrics();
};

export const getRequestHistory = (): NetworkRequest[] => {
  return networkOptimizer.getRequestHistory();
};

export const generateNetworkReport = (): string => {
  return networkOptimizer.generateReport();
}; 