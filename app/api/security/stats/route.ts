import { NextResponse } from 'next/server';
import { threatDetectionService } from '@/lib/security/enhanced-threat-detection';

export async function GET() {
  try {
    const stats = threatDetectionService.getThreatStats();
    
    return NextResponse.json(stats, {
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
      },
    });
  } catch (error) {
    console.error('Security stats error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch security statistics' },
      { status: 500 }
    );
  }
}

