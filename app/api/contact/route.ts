import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';

// Contact form validation schema
const contactSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters').max(100, 'Name must be less than 100 characters'),
  email: z.string().email('Invalid email address'),
  subject: z.string().min(5, 'Subject must be at least 5 characters').max(200, 'Subject must be less than 200 characters'),
  message: z.string().min(10, 'Message must be at least 10 characters').max(1000, 'Message must be less than 1000 characters'),
  honeypot: z.string().max(0, 'Invalid submission'), // Honeypot field for spam protection
});

export type ContactFormData = z.infer<typeof contactSchema>;

// Rate limiting configuration
const RATE_LIMIT_WINDOW = 60 * 1000; // 1 minute
const MAX_REQUESTS_PER_WINDOW = 5;

// In-memory rate limiting (use Redis in production)
const rateLimitMap = new Map<string, { count: number; resetTime: number }>();

function isRateLimited(identifier: string): boolean {
  const now = Date.now();
  const record = rateLimitMap.get(identifier);

  if (!record || now > record.resetTime) {
    rateLimitMap.set(identifier, { count: 1, resetTime: now + RATE_LIMIT_WINDOW });
    return false;
  }

  if (record.count >= MAX_REQUESTS_PER_WINDOW) {
    return true;
  }

  record.count++;
  return false;
}

function getClientIdentifier(req: NextRequest): string {
  // Use IP address for rate limiting
  const forwarded = req.headers.get('x-forwarded-for');
  const ip = forwarded ? forwarded.split(',')[0] : req.ip || 'unknown';
  return ip;
}

export async function POST(request: NextRequest) {
  try {
    // Rate limiting check
    const clientId = getClientIdentifier(request);
    if (isRateLimited(clientId)) {
      return NextResponse.json(
        { error: 'Too many requests. Please try again later.' },
        { status: 429 }
      );
    }

    // Parse and validate request body
    const body = await request.json();
    
    const validationResult = contactSchema.safeParse(body);
    if (!validationResult.success) {
      const errors = validationResult.error.errors.map(err => ({
        field: err.path.join('.'),
        message: err.message,
      }));

      return NextResponse.json(
        { 
          error: 'Validation failed',
          details: errors 
        },
        { status: 400 }
      );
    }

    const { name, email, subject, message } = validationResult.data;

    // Additional security checks
    if (message.includes('<script>') || message.includes('javascript:')) {
      return NextResponse.json(
        { error: 'Invalid message content' },
        { status: 400 }
      );
    }

    // Simulate processing (replace with actual email service)
    await processContactForm({ name, email, subject, message });

    // Log successful submission (use proper logging service in production)
    console.log(`Contact form submitted by ${email}: ${subject}`);

    return NextResponse.json(
      { 
        success: true,
        message: 'Thank you for your message. We will get back to you soon!' 
      },
      { status: 200 }
    );

  } catch (error) {
    // Log error (use proper logging service in production)
    console.error('Contact form error:', error);

    // Don't expose internal errors to client
    return NextResponse.json(
      { error: 'Internal server error. Please try again later.' },
      { status: 500 }
    );
  }
}

// Simulate contact form processing
async function processContactForm(data: ContactFormData): Promise<void> {
  // Simulate async processing
  await new Promise(resolve => setTimeout(resolve, 100));
  
  // In production, this would:
  // 1. Send email notification
  // 2. Store in database
  // 3. Trigger webhook if configured
  // 4. Send confirmation email to user
  
  // For now, just simulate success
  if (Math.random() < 0.1) { // 10% chance of failure for testing
    throw new Error('Simulated processing error');
  }
}

// OPTIONS method for CORS preflight
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  });
}





