import { NextRequest, NextResponse } from 'next/server';
import { advancedSecurityResilienceManager } from '@/lib/security/advanced-security-resilience';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const action = searchParams.get('action');

    switch (action) {
      case 'stats':
        const stats = await advancedSecurityResilienceManager.getResilienceStats();
        return NextResponse.json({ success: true, data: stats });

      case 'resilience':
        const resilienceId = searchParams.get('id');
        if (!resilienceId) {
          return NextResponse.json({ error: 'Resilience ID required' }, { status: 400 });
        }
        const resilience = await advancedSecurityResilienceManager.getSecurityResilience(resilienceId);
        return NextResponse.json({ success: true, data: resilience });

      case 'disaster_recovery':
        const drId = searchParams.get('id');
        if (!drId) {
          return NextResponse.json({ error: 'Disaster recovery ID required' }, { status: 400 });
        }
        const disasterRecovery = await advancedSecurityResilienceManager.getDisasterRecovery(drId);
        return NextResponse.json({ success: true, data: disasterRecovery });

      default:
        return NextResponse.json({ error: 'Invalid action' }, { status: 400 });
    }
  } catch (error) {
    console.error('Resilience API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { action, data } = body;

    switch (action) {
      case 'add_resilience':
        const resilience = await advancedSecurityResilienceManager.addSecurityResilience(data);
        return NextResponse.json({ success: true, data: resilience });

      case 'add_disaster_recovery':
        const disasterRecovery = await advancedSecurityResilienceManager.addDisasterRecovery(data);
        return NextResponse.json({ success: true, data: disasterRecovery });

      case 'execute_test':
        const testResults = await advancedSecurityResilienceManager.executeDisasterRecoveryTest(data.id, data.testType);
        return NextResponse.json({ success: true, data: testResults });

      case 'monitor_resilience':
        const monitoring = await advancedSecurityResilienceManager.monitorResilience(data.id);
        return NextResponse.json({ success: true, data: monitoring });

      default:
        return NextResponse.json({ error: 'Invalid action' }, { status: 400 });
    }
  } catch (error) {
    console.error('Resilience API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
