import { NextResponse } from 'next/server';
import { securityMonitoring } from '@/lib/security/security-monitoring';

export async function GET() {
  try {
    const stats = securityMonitoring.getMonitoringStats();
    
    return NextResponse.json(stats, {
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
      },
    });
  } catch (error) {
    console.error('Security monitoring error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch security monitoring data' },
      { status: 500 }
    );
  }
}
