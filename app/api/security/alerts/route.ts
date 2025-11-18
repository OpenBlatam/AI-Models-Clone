import { NextResponse } from 'next/server';
import { securityMonitoring } from '@/lib/security/security-monitoring';

export async function GET() {
  try {
    const alerts = securityMonitoring.getAlerts();
    
    return NextResponse.json(alerts, {
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
      },
    });
  } catch (error) {
    console.error('Security alerts error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch security alerts' },
      { status: 500 }
    );
  }
}
