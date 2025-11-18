import { NextRequest, NextResponse } from 'next/server';
import { cacheService } from '@/lib/cache/cache-service';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { endpoints, ttl = 300, strategy = 'cache_first' } = body;

    // Default endpoints to warm if none provided
    const defaultEndpoints = [
      { path: '/api/health', method: 'GET' },
      { path: '/api/user', method: 'GET' },
      { path: '/api/notes', method: 'GET' },
      { path: '/api/notifications', method: 'GET' },
    ];

    const endpointsToWarm = endpoints || defaultEndpoints;

    // Create data fetcher function
    const dataFetcher = async (endpoint: any) => {
      try {
        const url = new URL(endpoint.path, 'http://localhost:3000');
        const response = await fetch(url.toString(), {
          method: endpoint.method,
          headers: {
            'Content-Type': 'application/json',
            ...endpoint.headers,
          },
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return response;
      } catch (error) {
        console.error(`Failed to fetch ${endpoint.path}:`, error);
        throw error;
      }
    };

    // Warm the cache
    const warmedCount = await cacheService.warmCache({
      keys: endpointsToWarm.map((ep: any) => `${ep.method}:${ep.path}`),
      dataFetcher: async (key) => {
        const [method, path] = key.split(':');
        const endpoint = endpointsToWarm.find((ep: any) => ep.method === method && ep.path === path);
        if (endpoint) {
          const response = await dataFetcher(endpoint);
          return await response.json();
        }
        throw new Error(`Endpoint not found for key: ${key}`);
      },
      ttl,
      strategy: strategy as any,
    });

    return NextResponse.json({
      success: true,
      count: warmedCount,
      message: `Cache warmed with ${warmedCount} entries`,
      endpoints: endpointsToWarm,
    });
  } catch (error) {
    console.error('Cache warming error:', error);
    return NextResponse.json(
      { error: 'Failed to warm cache' },
      { status: 500 }
    );
  }
}

