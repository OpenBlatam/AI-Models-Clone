import { NextRequest, NextResponse } from 'next/server';
import { advancedSecurityResilienceManager } from '@/lib/security/advanced-security-resilience';

export async function GET(request: NextRequest) {
  try {
    const stats = await advancedSecurityResilienceManager.getResilienceStats();
    
    return NextResponse.json(stats);
  } catch (error) {
    console.error('Error fetching resilience stats:', error);
    return NextResponse.json(
      { error: 'Failed to fetch resilience stats' },
      { status: 500 }
    );
  }
}
