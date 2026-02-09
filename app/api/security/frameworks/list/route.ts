import { NextRequest, NextResponse } from 'next/server';
import { advancedSecurityGovernanceManager } from '@/lib/security/advanced-security-governance';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const filters = {
      type: searchParams.get('type') || undefined,
      category: searchParams.get('category') || undefined,
      status: searchParams.get('status') || undefined,
    };

    const frameworks = await advancedSecurityGovernanceManager.listFrameworks(filters);
    
    return NextResponse.json(frameworks);
  } catch (error) {
    console.error('Error fetching frameworks list:', error);
    return NextResponse.json(
      { error: 'Failed to fetch frameworks list' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const framework = await advancedSecurityGovernanceManager.createFramework(body);
    
    return NextResponse.json(framework, { status: 201 });
  } catch (error) {
    console.error('Error creating framework:', error);
    return NextResponse.json(
      { error: 'Failed to create framework' },
      { status: 500 }
    );
  }
}
