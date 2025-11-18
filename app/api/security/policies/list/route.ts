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

    const policies = await advancedSecurityGovernanceManager.listPolicies(filters);
    
    return NextResponse.json(policies);
  } catch (error) {
    console.error('Error fetching policies list:', error);
    return NextResponse.json(
      { error: 'Failed to fetch policies list' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const policy = await advancedSecurityGovernanceManager.createPolicy(body);
    
    return NextResponse.json(policy, { status: 201 });
  } catch (error) {
    console.error('Error creating policy:', error);
    return NextResponse.json(
      { error: 'Failed to create policy' },
      { status: 500 }
    );
  }
}
