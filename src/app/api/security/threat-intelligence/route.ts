import { NextRequest, NextResponse } from 'next/server';
import { ultimateSecurity } from '@/lib/security/ultimate-security-system';
import { threatIntelligence } from '@/lib/security/threat-intelligence';

// Threat intelligence API endpoint
export async function GET(request: NextRequest) {
  try {
    // Process request through security system
    const securityResult = await ultimateSecurity.processRequest(request);
    
    if (!securityResult.allowed) {
      return securityResult.response!;
    }
    
    // Get threat intelligence data
    const threatData = threatIntelligence.getThreatData();
    const metrics = threatIntelligence.getMetrics();
    
    // Get query parameters
    const { searchParams } = new URL(request.url);
    const feed = searchParams.get('feed');
    const severity = searchParams.get('severity');
    const timeRange = searchParams.get('timeRange') || '24h';
    
    // Filter threat data
    let filteredData = threatData;
    
    if (feed) {
      if (filteredData?.feeds) {
        filteredData.feeds = filteredData.feeds.filter((f: any) => 
          f.name.toLowerCase().includes(feed.toLowerCase())
        );
      }
    }
    
    if (severity) {
      if (filteredData?.threats) {
        filteredData.threats = filteredData.threats.filter((t: any) => 
          t.severity === severity
        );
      }
    }
    
    if (timeRange) {
      const hours = timeRange === '1h' ? 1 : timeRange === '24h' ? 24 : timeRange === '7d' ? 168 : 24;
      const cutoffTime = new Date(Date.now() - hours * 60 * 60 * 1000);
      
      if (filteredData?.threats) {
        filteredData.threats = filteredData.threats.filter((t: any) => 
          new Date(t.timestamp) >= cutoffTime
        );
      }
    }
    
    return NextResponse.json({
      status: 'success',
      timestamp: new Date().toISOString(),
      data: {
        threatIntelligence: filteredData,
        metrics,
        filters: {
          feed,
          severity,
          timeRange,
        },
        security: {
          threatLevel: securityResult.threatLevel,
          riskScore: securityResult.riskScore,
          aiAnalysis: securityResult.aiAnalysis,
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

// Analyze threat
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // Process request through security system
    const securityResult = await ultimateSecurity.processRequest(request);
    
    if (!securityResult.allowed) {
      return securityResult.response!;
    }
    
    // Validate analysis parameters
    if (!body.ipAddress && !body.domain && !body.hash) {
      return NextResponse.json(
        { error: 'IP address, domain, or hash is required' },
        { status: 400 }
      );
    }
    
    // Analyze threat
    const analysisResult = await threatIntelligence.analyzeThreat({
      ipAddress: body.ipAddress,
      domain: body.domain,
      hash: body.hash,
      userAgent: body.userAgent,
      url: body.url,
    });
    
    return NextResponse.json({
      status: 'success',
      message: 'Threat analysis completed',
      analysis: analysisResult,
      timestamp: new Date().toISOString(),
      security: {
        threatLevel: securityResult.threatLevel,
        riskScore: securityResult.riskScore,
        aiAnalysis: securityResult.aiAnalysis,
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

// Update threat intelligence feeds
export async function PUT(request: NextRequest) {
  try {
    // Process request through security system
    const securityResult = await ultimateSecurity.processRequest(request);
    
    if (!securityResult.allowed) {
      return securityResult.response!;
    }
    
    const body = await request.json();
    
    // Validate update parameters
    if (!body.feeds || !Array.isArray(body.feeds)) {
      return NextResponse.json(
        { error: 'Feeds array is required' },
        { status: 400 }
      );
    }
    
    // Update threat intelligence feeds
    const updateResult = await threatIntelligence.updateFeeds(body.feeds);
    
    if (!updateResult.success) {
      return NextResponse.json(
        {
          status: 'failed',
          error: 'Failed to update threat intelligence feeds',
          details: updateResult.error,
        },
        { status: 400 }
      );
    }
    
    return NextResponse.json({
      status: 'success',
      message: 'Threat intelligence feeds updated',
      updatedFeeds: updateResult.updatedFeeds,
      timestamp: new Date().toISOString(),
      security: {
        threatLevel: securityResult.threatLevel,
        riskScore: securityResult.riskScore,
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








