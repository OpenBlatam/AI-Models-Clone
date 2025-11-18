import { NextRequest, NextResponse } from 'next/server';
import { devSecOpsSecurityManager } from '@/lib/security/devsecops-security';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const action = searchParams.get('action');

    switch (action) {
      case 'stats':
        const stats = await devSecOpsSecurityManager.getDevSecOpsStats();
        return NextResponse.json({ success: true, data: stats });

      default:
        return NextResponse.json({ error: 'Invalid action' }, { status: 400 });
    }
  } catch (error) {
    console.error('DevSecOps Security API error:', error);
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
      case 'add_pipeline':
        const pipeline = await devSecOpsSecurityManager.addDevSecOpsPipeline(data);
        return NextResponse.json({ success: true, data: pipeline });

      default:
        return NextResponse.json({ error: 'Invalid action' }, { status: 400 });
    }
  } catch (error) {
    console.error('DevSecOps Security API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
