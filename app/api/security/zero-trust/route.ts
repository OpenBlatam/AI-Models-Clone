import { NextRequest, NextResponse } from 'next/server';
import { zeroTrustSecurity } from '@/lib/security/zero-trust-security';
import { z } from 'zod';

const TrustScoreRequestSchema = z.object({
  userId: z.string(),
  deviceId: z.string(),
  sessionId: z.string(),
});

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { userId, deviceId, sessionId } = TrustScoreRequestSchema.parse(body);
    
    // Create security context
    const context = await zeroTrustSecurity.createSecurityContext(userId, deviceId, sessionId);
    
    // Calculate trust score
    const trustScore = await zeroTrustSecurity.calculateTrustScore(userId, deviceId, sessionId);
    
    return NextResponse.json({
      context,
      trustScore,
      shouldGrantAccess: zeroTrustSecurity.shouldGrantAccess(sessionId),
      riskAssessment: zeroTrustSecurity.getRiskAssessment(sessionId),
    });
  } catch (error) {
    console.error('Zero trust security error:', error);
    
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Invalid request data', details: error.errors },
        { status: 400 }
      );
    }
    
    return NextResponse.json(
      { error: 'Failed to process zero trust request' },
      { status: 500 }
    );
  }
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const sessionId = searchParams.get('sessionId');
    
    if (!sessionId) {
      return NextResponse.json(
        { error: 'Session ID is required' },
        { status: 400 }
      );
    }
    
    const trustScore = zeroTrustSecurity.getTrustScore(sessionId);
    const context = zeroTrustSecurity.getSecurityContext(sessionId);
    const riskAssessment = zeroTrustSecurity.getRiskAssessment(sessionId);
    
    return NextResponse.json({
      trustScore,
      context,
      riskAssessment,
    });
  } catch (error) {
    console.error('Zero trust GET error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch zero trust data' },
      { status: 500 }
    );
  }
}
