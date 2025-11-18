import { NextRequest, NextResponse } from 'next/server';
import { advancedSecurityResilienceManager } from '@/lib/security/advanced-security-resilience';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const filters = {
      type: searchParams.get('type') || undefined,
      status: searchParams.get('status') || undefined,
      priority: searchParams.get('priority') || undefined,
    };

    const disasterRecovery = await advancedSecurityResilienceManager.listDisasterRecovery(filters);
    
    return NextResponse.json(disasterRecovery);
  } catch (error) {
    console.error('Error fetching disaster recovery list:', error);
    return NextResponse.json(
      { error: 'Failed to fetch disaster recovery list' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const disasterRecovery = await advancedSecurityResilienceManager.createDisasterRecovery(body);
    
    return NextResponse.json(disasterRecovery, { status: 201 });
  } catch (error) {
    console.error('Error creating disaster recovery:', error);
    return NextResponse.json(
      { error: 'Failed to create disaster recovery' },
      { status: 500 }
    );
  }
}
