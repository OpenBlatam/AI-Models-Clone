import { NextRequest, NextResponse } from 'next/server';
import { ultimateSecurity } from '@/lib/security/ultimate-security-system';

// Security dashboard API endpoint
export async function GET(request: NextRequest) {
  try {
    // Process request through security system
    const securityResult = await ultimateSecurity.processRequest(request);
    
    if (!securityResult.allowed) {
      return securityResult.response!;
    }
    
    // Get dashboard data
    const dashboardData = ultimateSecurity.getDashboardData();
    const metrics = ultimateSecurity.getMetrics();
    
    // Get query parameters for filtering
    const { searchParams } = new URL(request.url);
    const timeRange = searchParams.get('timeRange') || '24h';
    const severity = searchParams.get('severity');
    const type = searchParams.get('type');
    
    // Filter dashboard data based on parameters
    let filteredData = dashboardData;
    
    if (timeRange) {
      const hours = timeRange === '1h' ? 1 : timeRange === '24h' ? 24 : timeRange === '7d' ? 168 : 24;
      const cutoffTime = new Date(Date.now() - hours * 60 * 60 * 1000);
      
      if (filteredData?.events) {
        filteredData.events = filteredData.events.filter((event: any) => 
          new Date(event.timestamp) >= cutoffTime
        );
      }
    }
    
    if (severity) {
      if (filteredData?.events) {
        filteredData.events = filteredData.events.filter((event: any) => 
          event.severity === severity
        );
      }
    }
    
    if (type) {
      if (filteredData?.events) {
        filteredData.events = filteredData.events.filter((event: any) => 
          event.type === type
        );
      }
    }
    
    return NextResponse.json({
      status: 'success',
      timestamp: new Date().toISOString(),
      data: {
        dashboard: filteredData,
        metrics,
        filters: {
          timeRange,
          severity,
          type,
        },
        security: {
          threatLevel: securityResult.threatLevel,
          riskScore: securityResult.riskScore,
          trustScore: securityResult.trustScore,
          securityLayers: securityResult.securityLayers,
        },
      },
    });
    
  } catch (error) {
    return NextResponse.json(
      {
        status: 'error',
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    );
  }
}

// Create security event
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // Process request through security system
    const securityResult = await ultimateSecurity.processRequest(request);
    
    if (!securityResult.allowed) {
      return securityResult.response!;
    }
    
    // Validate event data
    if (!body.type || !body.severity) {
      return NextResponse.json(
        { error: 'Event type and severity are required' },
        { status: 400 }
      );
    }
    
    // Create security event
    const eventId = `event_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    const event = {
      id: eventId,
      type: body.type,
      severity: body.severity,
      source: body.source || 'api',
      details: body.details || {},
      timestamp: new Date().toISOString(),
      resolved: false,
      tags: body.tags || [],
    };
    
    return NextResponse.json({
      status: 'success',
      message: 'Security event created',
      event,
      timestamp: new Date().toISOString(),
    });
    
  } catch (error) {
    return NextResponse.json(
      {
        status: 'error',
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    );
  }
}








