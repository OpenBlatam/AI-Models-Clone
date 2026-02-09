import { NextRequest, NextResponse } from 'next/server';
import { securityTestingFramework } from '@/lib/security/security-testing-framework';

// GET /api/security/test - Get available security tests
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const category = searchParams.get('category');
    const severity = searchParams.get('severity');
    
    let tests = securityTestingFramework.getTests();
    
    // Filter by category
    if (category) {
      tests = tests.filter(test => test.category === category);
    }
    
    // Filter by severity
    if (severity) {
      tests = tests.filter(test => test.severity === severity);
    }
    
    return NextResponse.json({
      success: true,
      data: {
        tests,
        total: tests.length,
        categories: [...new Set(securityTestingFramework.getTests().map(t => t.category))],
        severities: [...new Set(securityTestingFramework.getTests().map(t => t.severity))],
      },
    });
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to get security tests',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}

// POST /api/security/test - Run security tests
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { 
      baseUrl = 'http://localhost:3000',
      testIds = [],
      category = null,
      severity = null,
      parallel = false 
    } = body;
    
    let results;
    
    if (testIds.length > 0) {
      // Run specific tests
      results = [];
      for (const testId of testIds) {
        const test = securityTestingFramework.getTest(testId);
        if (test) {
          const result = await securityTestingFramework.runTest(test, baseUrl);
          results.push(result);
        }
      }
    } else {
      // Run all tests or filtered tests
      if (category || severity) {
        let tests = securityTestingFramework.getTests();
        
        if (category) {
          tests = tests.filter(test => test.category === category);
        }
        
        if (severity) {
          tests = tests.filter(test => test.severity === severity);
        }
        
        results = [];
        for (const test of tests) {
          const result = await securityTestingFramework.runTest(test, baseUrl);
          results.push(result);
        }
      } else {
        // Run all tests
        results = await securityTestingFramework.runAllTests(baseUrl);
      }
    }
    
    const summary = securityTestingFramework.getTestSummary();
    
    return NextResponse.json({
      success: true,
      data: {
        results,
        summary,
        timestamp: new Date().toISOString(),
      },
    });
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to run security tests',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}

// GET /api/security/test/results - Get test results
export async function GET_RESULTS(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const format = searchParams.get('format') || 'json';
    
    const results = securityTestingFramework.getResults();
    const summary = securityTestingFramework.getTestSummary();
    
    if (format === 'csv') {
      const csv = securityTestingFramework.exportResults('csv');
      return new NextResponse(csv, {
        headers: {
          'Content-Type': 'text/csv',
          'Content-Disposition': 'attachment; filename="security-test-results.csv"',
        },
      });
    } else if (format === 'html') {
      const html = securityTestingFramework.exportResults('html');
      return new NextResponse(html, {
        headers: {
          'Content-Type': 'text/html',
        },
      });
    } else {
      return NextResponse.json({
        success: true,
        data: {
          results,
          summary,
          timestamp: new Date().toISOString(),
        },
      });
    }
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to get test results',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}

// DELETE /api/security/test/results - Clear test results
export async function DELETE(request: NextRequest) {
  try {
    securityTestingFramework.clearResults();
    
    return NextResponse.json({
      success: true,
      message: 'Test results cleared successfully',
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to clear test results',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}
