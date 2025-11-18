import { NextResponse } from 'next/server';
import { securityCompliance } from '@/lib/security/security-compliance';

export async function GET() {
  try {
    const controls = securityCompliance.getControls();
    
    return NextResponse.json(controls, {
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
      },
    });
  } catch (error) {
    console.error('Security compliance controls error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch security controls' },
      { status: 500 }
    );
  }
}
