import { NextResponse } from 'next/server';
import { securityOrchestration } from '@/lib/security/security-orchestration';

export async function GET() {
  try {
    const playbooks = securityOrchestration.getPlaybooks();
    
    return NextResponse.json(playbooks, {
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
      },
    });
  } catch (error) {
    console.error('Security orchestration playbooks error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch security playbooks' },
      { status: 500 }
    );
  }
}
