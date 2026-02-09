import { NextResponse } from 'next/server';
import { securityAnalytics } from '@/lib/security/security-analytics';

export async function GET() {
  try {
    const dashboardData = securityAnalytics.getDashboardData();
    
    return NextResponse.json(dashboardData, {
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
      },
    });
  } catch (error) {
    console.error('Security analytics error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch security analytics' },
      { status: 500 }
    );
  }
}
