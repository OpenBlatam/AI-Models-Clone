import { NextRequest, NextResponse } from 'next/server';
import { advancedAISecurityManager } from '@/lib/security/advanced-ai-security';

export async function GET(request: NextRequest) {
  try {
    const stats = await advancedAISecurityManager.getAISecurityStats();
    
    return NextResponse.json(stats);
  } catch (error) {
    console.error('Error fetching AI security stats:', error);
    return NextResponse.json(
      { error: 'Failed to fetch AI security stats' },
      { status: 500 }
    );
  }
}
