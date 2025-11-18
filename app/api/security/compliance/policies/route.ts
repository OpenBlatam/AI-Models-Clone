import { NextResponse } from 'next/server';
import { securityCompliance } from '@/lib/security/security-compliance';

export async function GET() {
  try {
    const policies = securityCompliance.getPolicies();
    
    return NextResponse.json(policies, {
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
      },
    });
  } catch (error) {
    console.error('Security compliance policies error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch security policies' },
      { status: 500 }
    );
  }
}
