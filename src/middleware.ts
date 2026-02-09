import { NextRequest, NextResponse } from 'next/server';
import { ultimateSecurity } from '@/lib/security/ultimate-security-system';

// Main Next.js middleware that integrates all security layers
export async function middleware(request: NextRequest) {
  try {
    // Process request through ultimate security system
    const securityResult = await ultimateSecurity.processRequest(request);
    
    // If request is blocked by security system
    if (!securityResult.allowed) {
      return securityResult.response!;
    }
    
    // Add security headers to response
    const response = NextResponse.next();
    
    // Add comprehensive security headers
    response.headers.set('X-Security-Status', 'protected');
    response.headers.set('X-Threat-Level', securityResult.threatLevel);
    response.headers.set('X-Risk-Score', securityResult.riskScore.toString());
    response.headers.set('X-Trust-Score', securityResult.trustScore.toString());
    response.headers.set('X-Biometric-Verified', securityResult.biometricVerified.toString());
    response.headers.set('X-Quantum-Encrypted', securityResult.quantumEncrypted.toString());
    response.headers.set('X-Processing-Time', securityResult.processingTime.toString());
    response.headers.set('X-Security-Layers', securityResult.securityLayers.join(','));
    
    // Add blockchain hash if available
    if (securityResult.blockchainHash) {
      response.headers.set('X-Blockchain-Hash', securityResult.blockchainHash);
    }
    
    // Add AI analysis confidence if available
    if (securityResult.aiAnalysis) {
      response.headers.set('X-AI-Confidence', securityResult.aiAnalysis.confidence.toString());
    }
    
    // Add compliance flags
    if (securityResult.complianceFlags.length > 0) {
      response.headers.set('X-Compliance-Flags', securityResult.complianceFlags.join(','));
    }
    
    // Add security events
    if (securityResult.securityEvents.length > 0) {
      response.headers.set('X-Security-Events', securityResult.securityEvents.join(','));
    }
    
    return response;
    
  } catch (error) {
    console.error('Security middleware error:', error);
    
    // Fallback security response
    return new NextResponse(
      JSON.stringify({
        error: 'Security processing failed',
        message: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString(),
      }),
      {
        status: 500,
        headers: {
          'Content-Type': 'application/json',
          'X-Security-Status': 'error',
        },
      }
    );
  }
}

// Configure which routes the middleware should run on
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     */
    '/((?!api|_next/static|_next/image|favicon.ico|public).*)',
  ],
};








