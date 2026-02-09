import { NextRequest, NextResponse } from 'next/server';
import { advancedAISecurityManager } from '@/lib/security/advanced-ai-security';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const filters = {
      type: searchParams.get('type') || undefined,
      category: searchParams.get('category') || undefined,
      severity: searchParams.get('severity') || undefined,
    };

    const insights = await advancedAISecurityManager.listInsights(filters);
    
    return NextResponse.json(insights);
  } catch (error) {
    console.error('Error fetching AI insights:', error);
    return NextResponse.json(
      { error: 'Failed to fetch AI insights' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const insight = await advancedAISecurityManager.createInsight(body);
    
    return NextResponse.json(insight, { status: 201 });
  } catch (error) {
    console.error('Error creating AI insight:', error);
    return NextResponse.json(
      { error: 'Failed to create AI insight' },
      { status: 500 }
    );
  }
}
