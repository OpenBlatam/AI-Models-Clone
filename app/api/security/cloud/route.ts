import { NextRequest, NextResponse } from 'next/server';
import { cloudSecurityManager } from '@/lib/security/cloud-security';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const action = searchParams.get('action');

    switch (action) {
      case 'stats':
        const stats = await cloudSecurityManager.getCloudStats();
        return NextResponse.json({ success: true, data: stats });

      default:
        return NextResponse.json({ error: 'Invalid action' }, { status: 400 });
    }
  } catch (error) {
    console.error('Cloud Security API error:', error);
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
      case 'add_provider':
        const provider = await cloudSecurityManager.addCloudProvider(data);
        return NextResponse.json({ success: true, data: provider });

      case 'add_service':
        const service = await cloudSecurityManager.addCloudService(data);
        return NextResponse.json({ success: true, data: service });

      case 'add_event':
        const event = await cloudSecurityManager.addSecurityEvent(data);
        return NextResponse.json({ success: true, data: event });

      case 'assess_compliance':
        const compliance = await cloudSecurityManager.assessCompliance(data.framework);
        return NextResponse.json({ success: true, data: compliance });

      case 'optimize_costs':
        const optimizations = await cloudSecurityManager.optimizeCosts(data.providerId);
        return NextResponse.json({ success: true, data: optimizations });

      default:
        return NextResponse.json({ error: 'Invalid action' }, { status: 400 });
    }
  } catch (error) {
    console.error('Cloud Security API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
