import { NextRequest, NextResponse } from 'next/server';
import { advancedSecurityResilienceManager } from '@/lib/security/advanced-security-resilience';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const filters = {
      type: searchParams.get('type') || undefined,
      category: searchParams.get('category') || undefined,
      status: searchParams.get('status') || undefined,
      priority: searchParams.get('priority') || undefined,
    };

    const resilience = await advancedSecurityResilienceManager.listResilience(filters);
    
    return NextResponse.json(resilience);
  } catch (error) {
    console.error('Error fetching resilience list:', error);
    return NextResponse.json(
      { error: 'Failed to fetch resilience list' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const resilience = await advancedSecurityResilienceManager.createResilience(body);
    
    return NextResponse.json(resilience, { status: 201 });
  } catch (error) {
    console.error('Error creating resilience:', error);
    return NextResponse.json(
      { error: 'Failed to create resilience' },
      { status: 500 }
    );
  }
}
