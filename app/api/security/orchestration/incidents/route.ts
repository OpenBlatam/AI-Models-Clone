import { NextResponse } from 'next/server';
import { securityOrchestration } from '@/lib/security/security-orchestration';

export async function GET() {
  try {
    const incidents = securityOrchestration.getIncidents();
    
    return NextResponse.json(incidents, {
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
      },
    });
  } catch (error) {
    console.error('Security orchestration incidents error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch security incidents' },
      { status: 500 }
    );
  }
}
