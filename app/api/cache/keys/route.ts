import { NextRequest, NextResponse } from 'next/server';
import { cacheService } from '@/lib/cache/cache-service';
import { redisClient } from '@/lib/cache/redis-client';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const pattern = searchParams.get('pattern') || '*';
    const limit = parseInt(searchParams.get('limit') || '100');

    // Get keys from Redis
    const keys = await redisClient.keys(pattern);
    
    // Get detailed information for each key
    const keyDetails = await Promise.all(
      keys.slice(0, limit).map(async (key) => {
        try {
          const ttl = await redisClient.ttl(key);
          const exists = await redisClient.exists(key);
          
          if (!exists) {
            return null;
          }

          // Get key size (approximate)
          const value = await redisClient.get(key);
          const size = value ? Buffer.byteLength(JSON.stringify(value), 'utf8') : 0;

          return {
            key,
            ttl,
            size,
            lastAccessed: Date.now(), // This would need to be tracked separately
            accessCount: 1, // This would need to be tracked separately
          };
        } catch (error) {
          console.error(`Error getting details for key ${key}:`, error);
          return null;
        }
      })
    );

    // Filter out null values
    const validKeys = keyDetails.filter((key): key is NonNullable<typeof key> => key !== null);

    return NextResponse.json(validKeys, {
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
      },
    });
  } catch (error) {
    console.error('Cache keys error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch cache keys' },
      { status: 500 }
    );
  }
}

