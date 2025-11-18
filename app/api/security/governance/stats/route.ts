import { NextRequest, NextResponse } from 'next/server';
import { advancedSecurityGovernanceManager } from '@/lib/security/advanced-security-governance';

export async function GET(request: NextRequest) {
  try {
    const stats = await advancedSecurityGovernanceManager.getGovernanceStats();
    
    return NextResponse.json(stats);
  } catch (error) {
    console.error('Error fetching governance stats:', error);
    return NextResponse.json(
      { error: 'Failed to fetch governance stats' },
      { status: 500 }
    );
  }
}
