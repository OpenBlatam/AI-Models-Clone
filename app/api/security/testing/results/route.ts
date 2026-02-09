import { NextRequest, NextResponse } from 'next/server';
import { securityTestSuite } from '@/lib/security/security-test-suite';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const testId = searchParams.get('testId');
    const category = searchParams.get('category');
    const status = searchParams.get('status');

    // Get test results
    const results = await securityTestSuite.runTestSuite();
    
    let filteredResults = results.results;

    // Filter by test ID
    if (testId) {
      filteredResults = filteredResults.filter(result => result.testId === testId);
    }

    // Filter by category
    if (category) {
      const test = results.tests.find(t => t.category === category);
      if (test) {
        filteredResults = filteredResults.filter(result => result.testId === test.id);
      }
    }

    // Filter by status
    if (status) {
      filteredResults = filteredResults.filter(result => result.status === status);
    }

    return NextResponse.json({
      success: true,
      data: {
        results: filteredResults,
        total: filteredResults.length,
        summary: {
          passed: filteredResults.filter(r => r.status === 'pass').length,
          failed: filteredResults.filter(r => r.status === 'fail').length,
          warnings: filteredResults.filter(r => r.status === 'warning').length,
          errors: filteredResults.filter(r => r.status === 'error').length,
        },
      },
      timestamp: new Date().toISOString(),
    });

  } catch (error) {
    console.error('Security test results error:', error);
    
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to get security test results',
        details: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    );
  }
}

