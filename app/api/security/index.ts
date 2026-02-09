/**
 * Security API Routes Index
 * Centralized routing for all security endpoints
 */

import { NextRequest, NextResponse } from 'next/server';
import { securityManager } from '@/lib/security';

// Security API route handler
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const action = searchParams.get('action');

    switch (action) {
      case 'status':
        return await getSecurityStatus();
      case 'config':
        return await getSecurityConfig();
      case 'metrics':
        return await getSecurityMetrics();
      case 'health':
        return await getSecurityHealth();
      default:
        return NextResponse.json(
          { error: 'Invalid action parameter' },
          { status: 400 }
        );
    }
  } catch (error) {
    console.error('Security API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const action = searchParams.get('action');
    const body = await request.json();

    switch (action) {
      case 'initialize':
        return await initializeSecurity();
      case 'update-config':
        return await updateSecurityConfig(body);
      case 'reset-config':
        return await resetSecurityConfig();
      default:
        return NextResponse.json(
          { error: 'Invalid action parameter' },
          { status: 400 }
        );
    }
  } catch (error) {
    console.error('Security API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

/**
 * Get security status
 */
async function getSecurityStatus() {
  try {
    const status = securityManager.getSecurityStatus();
    return NextResponse.json(status, {
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
      },
    });
  } catch (error) {
    console.error('Failed to get security status:', error);
    return NextResponse.json(
      { error: 'Failed to get security status' },
      { status: 500 }
    );
  }
}

/**
 * Get security configuration
 */
async function getSecurityConfig() {
  try {
    const config = securityManager.getConfig();
    return NextResponse.json(config);
  } catch (error) {
    console.error('Failed to get security config:', error);
    return NextResponse.json(
      { error: 'Failed to get security configuration' },
      { status: 500 }
    );
  }
}

/**
 * Get security metrics
 */
async function getSecurityMetrics() {
  try {
    const metrics = securityManager.getSecurityMetrics();
    return NextResponse.json(metrics, {
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
      },
    });
  } catch (error) {
    console.error('Failed to get security metrics:', error);
    return NextResponse.json(
      { error: 'Failed to get security metrics' },
      { status: 500 }
    );
  }
}

/**
 * Get security health
 */
async function getSecurityHealth() {
  try {
    const status = securityManager.getSecurityStatus();
    const health = {
      status: status.initialized ? 'healthy' : 'initializing',
      services: {
        biometric: status.services.biometric.enableWebAuthn ? 'active' : 'inactive',
        threatDetection: status.services.threatDetection.enableRealTimeMonitoring ? 'active' : 'inactive',
        zeroTrust: status.services.zeroTrust.enableContinuousVerification ? 'active' : 'inactive',
        encryption: status.services.encryption.enableEndToEndEncryption ? 'active' : 'inactive',
        monitoring: status.services.monitoring.enableRealTimeMonitoring ? 'active' : 'inactive',
        orchestration: status.services.orchestration.enableAutoResponse ? 'active' : 'inactive',
        compliance: status.services.compliance.enableComplianceMonitoring ? 'active' : 'inactive',
        intelligence: status.services.intelligence.enableThreatIntelligence ? 'active' : 'inactive',
      },
      timestamp: Date.now(),
    };
    
    return NextResponse.json(health, {
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
      },
    });
  } catch (error) {
    console.error('Failed to get security health:', error);
    return NextResponse.json(
      { error: 'Failed to get security health' },
      { status: 500 }
    );
  }
}

/**
 * Initialize security services
 */
async function initializeSecurity() {
  try {
    await securityManager.initialize();
    return NextResponse.json({ message: 'Security services initialized successfully' });
  } catch (error) {
    console.error('Failed to initialize security services:', error);
    return NextResponse.json(
      { error: 'Failed to initialize security services' },
      { status: 500 }
    );
  }
}

/**
 * Update security configuration
 */
async function updateSecurityConfig(config: any) {
  try {
    securityManager.updateConfig(config);
    return NextResponse.json({ message: 'Security configuration updated successfully' });
  } catch (error) {
    console.error('Failed to update security configuration:', error);
    return NextResponse.json(
      { error: 'Failed to update security configuration' },
      { status: 500 }
    );
  }
}

/**
 * Reset security configuration
 */
async function resetSecurityConfig() {
  try {
    // Reset to default configuration
    const defaultConfig = {
      biometric: {
        enableFingerprint: true,
        enableFaceRecognition: true,
        enableVoiceRecognition: true,
        enableBehavioralBiometrics: true,
        enableWebAuthn: true,
        minConfidence: 0.8,
        maxRetries: 3,
        timeout: 30000,
      },
      threatDetection: {
        enableMLDetection: true,
        enableBehavioralAnalysis: true,
        enableRealTimeMonitoring: true,
        maxThreatsPerMinute: 10,
        autoBlockThreshold: 0.8,
      },
      zeroTrust: {
        enableContinuousVerification: true,
        enableDeviceTrust: true,
        enableLocationVerification: true,
        enableBehavioralAnalysis: true,
        trustThreshold: 70,
        riskThreshold: 30,
      },
      encryption: {
        enableEndToEndEncryption: true,
        enableKeyRotation: true,
        enablePerfectForwardSecrecy: true,
        keyRotationInterval: 86400000,
        enableQuantumResistant: true,
      },
      monitoring: {
        enableRealTimeMonitoring: true,
        enableAnomalyDetection: true,
        enableThreatIntelligence: true,
        enableIncidentResponse: true,
        alertRetentionDays: 30,
      },
      orchestration: {
        enableAutoResponse: true,
        enablePlaybooks: true,
        enableWorkflows: true,
        enableEscalation: true,
        maxConcurrentWorkflows: 10,
      },
      compliance: {
        enableComplianceMonitoring: true,
        enablePolicyManagement: true,
        enableControlAssessment: true,
        enableAutomatedReporting: true,
        complianceFrameworks: ['ISO27001', 'SOC2', 'GDPR', 'HIPAA', 'PCI-DSS'],
      },
      intelligence: {
        enableThreatIntelligence: true,
        enableThreatHunting: true,
        enableIOCMatching: true,
        enableBehavioralAnalysis: true,
        enableAttribution: true,
      },
    };
    
    securityManager.updateConfig(defaultConfig);
    return NextResponse.json({ message: 'Security configuration reset to defaults' });
  } catch (error) {
    console.error('Failed to reset security configuration:', error);
    return NextResponse.json(
      { error: 'Failed to reset security configuration' },
      { status: 500 }
    );
  }
}
