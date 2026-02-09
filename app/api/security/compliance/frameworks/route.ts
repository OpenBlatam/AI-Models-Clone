import { NextResponse } from 'next/server';
import { securityCompliance } from '@/lib/security/security-compliance';

export async function GET() {
  try {
    const frameworks = securityCompliance.getFrameworks();
    
    return NextResponse.json(frameworks, {
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
      },
    });
  } catch (error) {
    console.error('Security compliance frameworks error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch compliance frameworks' },
      { status: 500 }
    );
  }
}
