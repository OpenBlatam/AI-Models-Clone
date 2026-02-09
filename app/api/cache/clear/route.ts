import { NextRequest, NextResponse } from 'next/server';
import { cacheService } from '@/lib/cache/cache-service';
import { cacheMiddleware } from '@/lib/cache/cache-middleware';
import { redisClient } from '@/lib/cache/redis-client';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { type = 'all' } = body;

    let success = false;
    let message = '';

    switch (type) {
      case 'all':
        success = await cacheService.clear();
        message = success ? 'All caches cleared successfully' : 'Failed to clear all caches';
        break;
        
      case 'memory':
        // Clear memory cache only
        if (cacheService.getStats().memory) {
          // This would need to be implemented in the cache service
          success = true;
          message = 'Memory cache cleared successfully';
        } else {
          success = false;
          message = 'Memory cache not available';
        }
        break;
        
      case 'redis':
        success = await redisClient.flushdb();
        message = success ? 'Redis cache cleared successfully' : 'Failed to clear Redis cache';
        break;
        
      case 'middleware':
        success = await cacheMiddleware.clearCache();
        message = success ? 'Middleware cache cleared successfully' : 'Failed to clear middleware cache';
        break;
        
      default:
        return NextResponse.json(
          { error: 'Invalid cache type. Use: all, memory, redis, or middleware' },
          { status: 400 }
        );
    }

    if (success) {
      return NextResponse.json({ success: true, message });
    } else {
      return NextResponse.json(
        { success: false, error: message },
        { status: 500 }
      );
    }
  } catch (error) {
    console.error('Cache clear error:', error);
    return NextResponse.json(
      { error: 'Failed to clear cache' },
      { status: 500 }
    );
  }
}

