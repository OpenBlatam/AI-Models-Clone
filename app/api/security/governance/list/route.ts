import { NextRequest, NextResponse } from 'next/server';
import { advancedSecurityGovernanceManager } from '@/lib/security/advanced-security-governance';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const filters = {
      type: searchParams.get('type') || undefined,
      category: searchParams.get('category') || undefined,
      status: searchParams.get('status') || undefined,
      owner: searchParams.get('owner') || undefined,
    };

    const governance = await advancedSecurityGovernanceManager.listGovernance(filters);
    
    return NextResponse.json(governance);
  } catch (error) {
    console.error('Error fetching governance list:', error);
    return NextResponse.json(
      { error: 'Failed to fetch governance list' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const governance = await advancedSecurityGovernanceManager.createGovernance(body);
    
    return NextResponse.json(governance, { status: 201 });
  } catch (error) {
    console.error('Error creating governance:', error);
    return NextResponse.json(
      { error: 'Failed to create governance' },
      { status: 500 }
    );
  }
}