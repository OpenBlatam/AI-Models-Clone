import { NextResponse } from 'next/server';
import { securityCompliance } from '@/lib/security/security-compliance';

export async function GET() {
  try {
    const dashboardData = securityCompliance.getComplianceDashboard();
    
    return NextResponse.json(dashboardData, {
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
      },
    });
  } catch (error) {
    console.error('Security compliance dashboard error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch compliance dashboard data' },
      { status: 500 }
    );
  }
}
