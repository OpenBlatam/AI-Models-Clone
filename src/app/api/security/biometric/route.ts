import { NextRequest, NextResponse } from 'next/server';
import { ultimateSecurity } from '@/lib/security/ultimate-security-system';
import { biometricAuth } from '@/lib/security/biometric-authentication';

// Biometric authentication API endpoint
export async function POST(request: NextRequest) {
  try {
    // Process request through security system
    const securityResult = await ultimateSecurity.processRequest(request);
    
    if (!securityResult.allowed) {
      return securityResult.response!;
    }
    
    const body = await request.json();
    
    // Validate biometric data
    if (!body.userId || !body.biometricData) {
      return NextResponse.json(
        { error: 'User ID and biometric data are required' },
        { status: 400 }
      );
    }
    
    const { userId, biometricData, sessionId } = body;
    
    // Verify biometric data
    const verificationResult = await biometricAuth.verifyBiometricData(
      userId,
      biometricData,
      sessionId
    );
    
    if (!verificationResult.success) {
      return NextResponse.json(
        {
          status: 'failed',
          error: 'Biometric verification failed',
          confidence: verificationResult.confidence,
          attempts: verificationResult.attempts,
          lockoutTime: verificationResult.lockoutTime,
        },
        { status: 401 }
      );
    }
    
    return NextResponse.json({
      status: 'success',
      message: 'Biometric verification successful',
      confidence: verificationResult.confidence,
      methods: verificationResult.methods,
      timestamp: new Date().toISOString(),
      security: {
        threatLevel: securityResult.threatLevel,
        trustScore: securityResult.trustScore,
        quantumEncrypted: securityResult.quantumEncrypted,
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

// Register biometric data
export async function PUT(request: NextRequest) {
  try {
    // Process request through security system
    const securityResult = await ultimateSecurity.processRequest(request);
    
    if (!securityResult.allowed) {
      return securityResult.response!;
    }
    
    const body = await request.json();
    
    // Validate registration data
    if (!body.userId || !body.biometricData || !body.methods) {
      return NextResponse.json(
        { error: 'User ID, biometric data, and methods are required' },
        { status: 400 }
      );
    }
    
    const { userId, biometricData, methods, metadata } = body;
    
    // Register biometric data
    const registrationResult = await biometricAuth.registerBiometricData(
      userId,
      biometricData,
      methods,
      metadata
    );
    
    if (!registrationResult.success) {
      return NextResponse.json(
        {
          status: 'failed',
          error: 'Biometric registration failed',
          details: registrationResult.error,
        },
        { status: 400 }
      );
    }
    
    return NextResponse.json({
      status: 'success',
      message: 'Biometric data registered successfully',
      registrationId: registrationResult.registrationId,
      methods: registrationResult.methods,
      timestamp: new Date().toISOString(),
      security: {
        threatLevel: securityResult.threatLevel,
        trustScore: securityResult.trustScore,
        quantumEncrypted: securityResult.quantumEncrypted,
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

// Get biometric status
export async function GET(request: NextRequest) {
  try {
    // Process request through security system
    const securityResult = await ultimateSecurity.processRequest(request);
    
    if (!securityResult.allowed) {
      return securityResult.response!;
    }
    
    const { searchParams } = new URL(request.url);
    const userId = searchParams.get('userId');
    
    if (!userId) {
      return NextResponse.json(
        { error: 'User ID is required' },
        { status: 400 }
      );
    }
    
    // Get biometric status
    const status = await biometricAuth.getBiometricStatus(userId);
    
    return NextResponse.json({
      status: 'success',
      data: {
        userId,
        biometricStatus: status,
        security: {
          threatLevel: securityResult.threatLevel,
          trustScore: securityResult.trustScore,
          biometricVerified: securityResult.biometricVerified,
        },
      },
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








