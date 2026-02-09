import { NextResponse } from 'next/server';
import { securityCompliance } from '@/lib/security/security-compliance';

export async function GET() {
  try {
    const assessments = securityCompliance.getAssessments();
    
    return NextResponse.json(assessments, {
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
      },
    });
  } catch (error) {
    console.error('Security compliance assessments error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch compliance assessments' },
      { status: 500 }
    );
  }
}
