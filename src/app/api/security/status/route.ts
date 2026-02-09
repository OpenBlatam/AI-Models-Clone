import { NextRequest, NextResponse } from 'next/server';
import { ultimateSecurity } from '@/lib/security/ultimate-security-system';

// Security status API endpoint
export async function GET(request: NextRequest) {
  try {
    // Process request through security system
    const securityResult = await ultimateSecurity.processRequest(request);
    
    if (!securityResult.allowed) {
      return securityResult.response!;
    }
    
    // Get comprehensive security metrics
    const metrics = ultimateSecurity.getMetrics();
    const dashboardData = ultimateSecurity.getDashboardData();
    const complianceStatus = ultimateSecurity.getComplianceStatus();
    
    return NextResponse.json({
      status: 'operational',
      timestamp: new Date().toISOString(),
      security: {
        threatLevel: securityResult.threatLevel,
        riskScore: securityResult.riskScore,
        trustScore: securityResult.trustScore,
        biometricVerified: securityResult.biometricVerified,
        quantumEncrypted: securityResult.quantumEncrypted,
        aiAnalysis: securityResult.aiAnalysis,
        blockchainHash: securityResult.blockchainHash,
        securityLayers: securityResult.securityLayers,
        processingTime: securityResult.processingTime,
      },
      metrics,
      dashboard: dashboardData,
      compliance: complianceStatus,
      system: {
        version: '2.0.0',
        uptime: process.uptime(),
        memory: process.memoryUsage(),
        platform: process.platform,
        nodeVersion: process.version,
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

// Update security configuration
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // Validate configuration
    if (!body.config) {
      return NextResponse.json(
        { error: 'Configuration is required' },
        { status: 400 }
      );
    }
    
    // Update security configuration
    ultimateSecurity.updateConfig(body.config);
    
    return NextResponse.json({
      status: 'success',
      message: 'Security configuration updated',
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








