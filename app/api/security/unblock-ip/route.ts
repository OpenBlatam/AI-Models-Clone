import { NextRequest, NextResponse } from 'next/server';
import { threatDetectionService } from '@/lib/security/enhanced-threat-detection';
import { z } from 'zod';

const UnblockIPSchema = z.object({
  ip: z.string().ip(),
});

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { ip } = UnblockIPSchema.parse(body);
    
    threatDetectionService.unblockIP(ip);
    
    return NextResponse.json(
      { message: `IP ${ip} unblocked successfully`, ip },
      { status: 200 }
    );
  } catch (error) {
    console.error('Unblock IP error:', error);
    
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Invalid IP address', details: error.errors },
        { status: 400 }
      );
    }
    
    return NextResponse.json(
      { error: 'Failed to unblock IP address' },
      { status: 500 }
    );
  }
}

