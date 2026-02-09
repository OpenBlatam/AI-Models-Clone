import { NextResponse } from 'next/server';
import openApiSpec from '@/lib/api-docs/openapi-spec';

export async function GET() {
  try {
    return NextResponse.json(openApiSpec, {
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'public, max-age=3600', // Cache for 1 hour
      },
    });
  } catch (error) {
    console.error('Error serving OpenAPI spec:', error);
    return NextResponse.json(
      { error: 'Failed to load API specification' },
      { status: 500 }
    );
  }
}


