import { NextRequest, NextResponse } from 'next/server';
import { securityPerformanceOptimizer } from '@/lib/security/security-performance-optimizer';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const timeRange = searchParams.get('timeRange') || '1h';
    const operation = searchParams.get('operation');

    // Get performance metrics
    const metrics = securityPerformanceOptimizer.getMetrics(operation || undefined);
    
    // Filter by time range
    const now = new Date();
    const timeRangeMs = getTimeRangeMs(timeRange);
    const filteredMetrics = metrics.filter(m => 
      now.getTime() - m.timestamp.getTime() <= timeRangeMs
    );

    // Calculate summary statistics
    const summary = {
      totalMetrics: filteredMetrics.length,
      averageLatency: calculateAverage(filteredMetrics.map(m => m.latency)),
      averageThroughput: calculateAverage(filteredMetrics.map(m => m.throughput)),
      averageErrorRate: calculateAverage(filteredMetrics.map(m => m.errorRate)),
      averageCacheHitRate: calculateAverage(filteredMetrics.map(m => m.cacheHitRate)),
      averageMemoryUsage: calculateAverage(filteredMetrics.map(m => m.memoryUsage)),
      averageCPUUsage: calculateAverage(filteredMetrics.map(m => m.cpuUsage)),
      latestMetrics: filteredMetrics[filteredMetrics.length - 1] || null,
    };

    return NextResponse.json({
      success: true,
      data: {
        metrics: filteredMetrics,
        summary,
        timeRange,
        generated_at: new Date().toISOString(),
      },
      timestamp: new Date().toISOString(),
    });

  } catch (error) {
    console.error('Security monitoring metrics error:', error);
    
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to get security monitoring metrics',
        details: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { operation, duration, memoryUsage, cpuUsage, cacheHitRate, throughput, errorRate, latency, queueSize, activeConnections, metadata } = body;

    // Create new metrics entry
    const metrics = {
      id: `metrics_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date(),
      operation: operation || 'unknown',
      duration: duration || 0,
      memoryUsage: memoryUsage || 0,
      cpuUsage: cpuUsage || 0,
      cacheHitRate: cacheHitRate || 0,
      throughput: throughput || 0,
      errorRate: errorRate || 0,
      latency: latency || 0,
      queueSize: queueSize || 0,
      activeConnections: activeConnections || 0,
      metadata: metadata || {},
    };

    // Store metrics (in real implementation, this would be stored in database)
    // For now, we'll just return success

    return NextResponse.json({
      success: true,
      data: {
        metrics,
        message: 'Metrics recorded successfully',
      },
      timestamp: new Date().toISOString(),
    });

  } catch (error) {
    console.error('Security monitoring metrics recording error:', error);
    
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to record security monitoring metrics',
        details: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    );
  }
}

// Helper functions
function getTimeRangeMs(timeRange: string): number {
  switch (timeRange) {
    case '5m':
      return 5 * 60 * 1000;
    case '15m':
      return 15 * 60 * 1000;
    case '1h':
      return 60 * 60 * 1000;
    case '6h':
      return 6 * 60 * 60 * 1000;
    case '24h':
      return 24 * 60 * 60 * 1000;
    case '7d':
      return 7 * 24 * 60 * 60 * 1000;
    default:
      return 60 * 60 * 1000; // Default to 1 hour
  }
}

function calculateAverage(values: number[]): number {
  if (values.length === 0) return 0;
  return values.reduce((sum, val) => sum + val, 0) / values.length;
}








