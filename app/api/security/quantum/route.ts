import { NextRequest, NextResponse } from 'next/server';
import { quantumSecurityManager } from '@/lib/security/quantum-security';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const action = searchParams.get('action');

    switch (action) {
      case 'stats':
        const stats = await quantumSecurityManager.getQuantumStats();
        return NextResponse.json({ success: true, data: stats });

      default:
        return NextResponse.json({ error: 'Invalid action' }, { status: 400 });
    }
  } catch (error) {
    console.error('Quantum Security API error:', error);
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
      case 'generate_key':
        const quantumKey = await quantumSecurityManager.generateQuantumKey(data.algorithm);
        return NextResponse.json({ success: true, data: quantumKey });

      case 'assess_readiness':
        const assessment = await quantumSecurityManager.assessQuantumReadiness(data.systemId);
        return NextResponse.json({ success: true, data: assessment });

      default:
        return NextResponse.json({ error: 'Invalid action' }, { status: 400 });
    }
  } catch (error) {
    console.error('Quantum Security API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
