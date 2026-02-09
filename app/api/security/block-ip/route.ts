import { NextRequest, NextResponse } from 'next/server';
import { threatDetectionService } from '@/lib/security/enhanced-threat-detection';
import { z } from 'zod';

const BlockIPSchema = z.object({
  ip: z.string().ip(),
  reason: z.string().min(1),
});

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { ip, reason } = BlockIPSchema.parse(body);
    
    threatDetectionService.blockIP(ip, reason);
    
    return NextResponse.json(
      { message: `IP ${ip} blocked successfully`, ip, reason },
      { status: 200 }
    );
  } catch (error) {
    console.error('Block IP error:', error);
    
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Invalid IP address or reason', details: error.errors },
        { status: 400 }
      );
    }
    
    return NextResponse.json(
      { error: 'Failed to block IP address' },
      { status: 500 }
    );
  }
}

