import { NextRequest, NextResponse } from 'next/server';
import { advancedAISecurityManager } from '@/lib/security/advanced-ai-security';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const filters = {
      type: searchParams.get('type') || undefined,
      category: searchParams.get('category') || undefined,
      status: searchParams.get('status') || undefined,
    };

    const models = await advancedAISecurityManager.listModels(filters);
    
    return NextResponse.json(models);
  } catch (error) {
    console.error('Error fetching AI models:', error);
    return NextResponse.json(
      { error: 'Failed to fetch AI models' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const model = await advancedAISecurityManager.createModel(body);
    
    return NextResponse.json(model, { status: 201 });
  } catch (error) {
    console.error('Error creating AI model:', error);
    return NextResponse.json(
      { error: 'Failed to create AI model' },
      { status: 500 }
    );
  }
}
