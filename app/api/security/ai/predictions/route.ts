import { NextRequest, NextResponse } from 'next/server';
import { advancedAISecurityManager } from '@/lib/security/advanced-ai-security';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const filters = {
      modelId: searchParams.get('modelId') || undefined,
      startDate: searchParams.get('startDate') ? new Date(searchParams.get('startDate')!) : undefined,
      endDate: searchParams.get('endDate') ? new Date(searchParams.get('endDate')!) : undefined,
    };

    const predictions = await advancedAISecurityManager.listPredictions(filters);
    
    return NextResponse.json(predictions);
  } catch (error) {
    console.error('Error fetching AI predictions:', error);
    return NextResponse.json(
      { error: 'Failed to fetch AI predictions' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const prediction = await advancedAISecurityManager.createPrediction(body);
    
    return NextResponse.json(prediction, { status: 201 });
  } catch (error) {
    console.error('Error creating AI prediction:', error);
    return NextResponse.json(
      { error: 'Failed to create AI prediction' },
      { status: 500 }
    );
  }
}
