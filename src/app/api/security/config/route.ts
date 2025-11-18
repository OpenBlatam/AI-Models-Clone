import { NextRequest, NextResponse } from 'next/server';
import { securityConfigManager } from '@/lib/security/security-config-manager';

// GET /api/security/config - Get current security configuration
export async function GET(request: NextRequest) {
  try {
    const config = securityConfigManager.getConfig();
    const summary = securityConfigManager.getConfigSummary();
    
    return NextResponse.json({
      success: true,
      data: {
        config,
        summary,
        timestamp: new Date().toISOString(),
      },
    });
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to get security configuration',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}

// PUT /api/security/config - Update security configuration
export async function PUT(request: NextRequest) {
  try {
    const body = await request.json();
    const { config, user } = body;
    
    if (!config) {
      return NextResponse.json(
        {
          success: false,
          error: 'Configuration data is required',
        },
        { status: 400 }
      );
    }
    
    // Validate configuration
    const validation = securityConfigManager.validateConfig(config);
    if (!validation.valid) {
      return NextResponse.json(
        {
          success: false,
          error: 'Invalid configuration',
          details: validation.errors,
        },
        { status: 400 }
      );
    }
    
    // Update configuration
    securityConfigManager.updateConfig(config, user || 'api');
    
    return NextResponse.json({
      success: true,
      message: 'Configuration updated successfully',
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to update security configuration',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}

// PATCH /api/security/config - Update specific configuration section
export async function PATCH(request: NextRequest) {
  try {
    const body = await request.json();
    const { section, updates, user } = body;
    
    if (!section || !updates) {
      return NextResponse.json(
        {
          success: false,
          error: 'Section and updates are required',
        },
        { status: 400 }
      );
    }
    
    // Update configuration section
    securityConfigManager.updateSection(section, updates, user || 'api');
    
    return NextResponse.json({
      success: true,
      message: `Configuration section '${section}' updated successfully`,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to update configuration section',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}

// POST /api/security/config/reset - Reset configuration to defaults
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { user } = body;
    
    // Reset configuration
    securityConfigManager.resetConfig(user || 'api');
    
    return NextResponse.json({
      success: true,
      message: 'Configuration reset to defaults successfully',
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to reset configuration',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}
