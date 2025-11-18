import { NextRequest, NextResponse } from 'next/server';
import { cacheService } from '@/lib/cache/cache-service';
import { redisClient } from '@/lib/cache/redis-client';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { keys } = body;

    if (!keys || !Array.isArray(keys) || keys.length === 0) {
      return NextResponse.json(
        { error: 'Keys array is required and must not be empty' },
        { status: 400 }
      );
    }

    let deletedCount = 0;
    const errors: string[] = [];

    // Delete keys from cache service
    for (const key of keys) {
      try {
        const success = await cacheService.delete(key);
        if (success) {
          deletedCount++;
        } else {
          errors.push(`Failed to delete key: ${key}`);
        }
      } catch (error) {
        errors.push(`Error deleting key ${key}: ${error}`);
      }
    }

    // Also delete from Redis directly (in case cache service doesn't handle it)
    try {
      const pipeline = redisClient.constructor.name === 'Cluster' 
        ? redisClient.pipeline() 
        : redisClient.pipeline();
      
      for (const key of keys) {
        pipeline.del(key);
      }
      
      const results = await pipeline.exec();
      if (results) {
        const redisDeletedCount = results.filter(([err, result]) => !err && result > 0).length;
        console.log(`Redis deleted ${redisDeletedCount} keys`);
      }
    } catch (error) {
      console.error('Redis batch delete error:', error);
    }

    return NextResponse.json({
      success: deletedCount > 0,
      deletedCount,
      totalRequested: keys.length,
      errors: errors.length > 0 ? errors : undefined,
    });
  } catch (error) {
    console.error('Cache delete error:', error);
    return NextResponse.json(
      { error: 'Failed to delete cache keys' },
      { status: 500 }
    );
  }
}

