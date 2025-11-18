import { NextResponse } from 'next/server';
import { securityOrchestration } from '@/lib/security/security-orchestration';

export async function GET() {
  try {
    const stats = securityOrchestration.getOrchestrationStats();
    
    return NextResponse.json(stats, {
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
      },
    });
  } catch (error) {
    console.error('Security orchestration stats error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch orchestration statistics' },
      { status: 500 }
    );
  }
}