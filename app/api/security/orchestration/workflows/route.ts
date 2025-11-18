import { NextResponse } from 'next/server';
import { securityOrchestration } from '@/lib/security/security-orchestration';

export async function GET() {
  try {
    const workflows = securityOrchestration.getWorkflows();
    
    return NextResponse.json(workflows, {
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
      },
    });
  } catch (error) {
    console.error('Security orchestration workflows error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch security workflows' },
      { status: 500 }
    );
  }
}
