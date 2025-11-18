import { NextRequest, NextResponse } from 'next/server';
import { securityAnalytics } from '@/lib/security/security-analytics';

// GET /api/security/analytics - Get security analytics
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const startDate = searchParams.get('startDate');
    const endDate = searchParams.get('endDate');
    
    let timeRange;
    if (startDate && endDate) {
      timeRange = {
        start: new Date(startDate),
        end: new Date(endDate),
      };
    }
    
    const analytics = await securityAnalytics.getAnalytics(timeRange);
    
    return NextResponse.json({
      success: true,
      data: analytics,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to get security analytics',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}

// GET /api/security/analytics/cache - Get cache status
export async function GET_CACHE(request: NextRequest) {
  try {
    const cacheStatus = securityAnalytics.getCacheStatus();
    
    return NextResponse.json({
      success: true,
      data: cacheStatus,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to get cache status',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}

// DELETE /api/security/analytics/cache - Clear analytics cache
export async function DELETE_CACHE(request: NextRequest) {
  try {
    securityAnalytics.clearCache();
    
    return NextResponse.json({
      success: true,
      message: 'Analytics cache cleared successfully',
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to clear analytics cache',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}
