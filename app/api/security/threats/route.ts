import { NextRequest, NextResponse } from 'next/server';
import { threatDetectionService } from '@/lib/security/enhanced-threat-detection';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const limit = parseInt(searchParams.get('limit') || '50');
    
    const threats = threatDetectionService.getRecentThreats(limit);
    
    return NextResponse.json(threats, {
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
      },
    });
  } catch (error) {
    console.error('Security threats error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch security threats' },
      { status: 500 }
    );
  }
}

