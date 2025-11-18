import { NextResponse } from 'next/server';
import { cacheService } from '@/lib/cache/cache-service';
import { cacheMiddleware } from '@/lib/cache/cache-middleware';
import { redisClient } from '@/lib/cache/redis-client';

export async function GET() {
  try {
    // Get cache service stats
    const serviceStats = cacheService.getStats();
    
    // Get middleware stats
    const middlewareStats = cacheMiddleware.getStats();
    
    // Get Redis client metrics
    const redisMetrics = redisClient.getMetrics();
    
    // Get Redis info
    const redisInfo = await redisClient.getInfo();
    
    // Get memory usage
    const memoryUsage = await redisClient.getMemoryUsage();

    // Combine all stats
    const stats = {
      memory: serviceStats.memory,
      redis: {
        ...redisMetrics,
        memoryUsage,
        info: redisInfo,
      },
      service: serviceStats.service,
      middleware: middlewareStats.middleware,
      config: {
        ...serviceStats.config,
        ...middlewareStats.config,
      },
      timestamp: new Date().toISOString(),
    };

    return NextResponse.json(stats, {
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
      },
    });
  } catch (error) {
    console.error('Cache stats error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch cache statistics' },
      { status: 500 }
    );
  }
}

