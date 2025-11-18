import { NextRequest, NextResponse } from 'next/server';
import { threatDetectionService } from '@/lib/security/enhanced-threat-detection';
import { z } from 'zod';

const SecurityRuleSchema = z.object({
  name: z.string().min(1),
  pattern: z.string().min(1),
  action: z.enum(['block', 'alert', 'log', 'rate_limit']),
  threshold: z.number().min(0).max(1),
  enabled: z.boolean().optional().default(true),
});

export async function GET() {
  try {
    const rules = threatDetectionService.getSecurityRules();
    
    return NextResponse.json(rules);
  } catch (error) {
    console.error('Security rules GET error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch security rules' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const validatedData = SecurityRuleSchema.parse(body);
    
    const newRule = threatDetectionService.addSecurityRule(validatedData);
    
    return NextResponse.json(newRule, { status: 201 });
  } catch (error) {
    console.error('Security rules POST error:', error);
    
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Invalid rule data', details: error.errors },
        { status: 400 }
      );
    }
    
    return NextResponse.json(
      { error: 'Failed to create security rule' },
      { status: 500 }
    );
  }
}

