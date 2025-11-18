import { NextRequest, NextResponse } from 'next/server';
import { securityPerformanceOptimizer } from '@/lib/security/security-performance-optimizer';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const status = searchParams.get('status');
    const severity = searchParams.get('severity');
    const type = searchParams.get('type');
    const limit = parseInt(searchParams.get('limit') || '50');

    // Get performance alerts
    let alerts = securityPerformanceOptimizer.getAlerts();
    
    // Filter alerts
    if (status) {
      alerts = alerts.filter(alert => alert.status === status);
    }
    if (severity) {
      alerts = alerts.filter(alert => alert.severity === severity);
    }
    if (type) {
      alerts = alerts.filter(alert => alert.type === type);
    }

    // Sort by timestamp (newest first)
    alerts.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());

    // Limit results
    alerts = alerts.slice(0, limit);

    // Calculate summary
    const summary = {
      total: alerts.length,
      active: alerts.filter(a => !a.resolved).length,
      acknowledged: alerts.filter(a => a.acknowledged && !a.resolved).length,
      resolved: alerts.filter(a => a.resolved).length,
      critical: alerts.filter(a => a.severity === 'critical').length,
      high: alerts.filter(a => a.severity === 'high').length,
      medium: alerts.filter(a => a.severity === 'medium').length,
      low: alerts.filter(a => a.severity === 'low').length,
    };

    return NextResponse.json({
      success: true,
      data: {
        alerts,
        summary,
        filters: { status, severity, type, limit },
        generated_at: new Date().toISOString(),
      },
      timestamp: new Date().toISOString(),
    });

  } catch (error) {
    console.error('Security monitoring alerts error:', error);
    
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to get security monitoring alerts',
        details: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { alertId, action } = body;

    if (!alertId || !action) {
      return NextResponse.json(
        {
          success: false,
          error: 'Missing required fields: alertId and action',
          timestamp: new Date().toISOString(),
        },
        { status: 400 }
      );
    }

    // Get alerts
    const alerts = securityPerformanceOptimizer.getAlerts();
    const alert = alerts.find(a => a.id === alertId);

    if (!alert) {
      return NextResponse.json(
        {
          success: false,
          error: 'Alert not found',
          timestamp: new Date().toISOString(),
        },
        { status: 404 }
      );
    }

    // Perform action
    switch (action) {
      case 'acknowledge':
        alert.acknowledged = true;
        break;
      case 'resolve':
        alert.resolved = true;
        alert.acknowledged = true;
        break;
      case 'unacknowledge':
        alert.acknowledged = false;
        break;
      case 'unresolve':
        alert.resolved = false;
        break;
      default:
        return NextResponse.json(
          {
            success: false,
            error: 'Invalid action. Supported actions: acknowledge, resolve, unacknowledge, unresolve',
            timestamp: new Date().toISOString(),
          },
          { status: 400 }
        );
    }

    return NextResponse.json({
      success: true,
      data: {
        alert,
        action,
        message: `Alert ${action}d successfully`,
      },
      timestamp: new Date().toISOString(),
    });

  } catch (error) {
    console.error('Security monitoring alert action error:', error);
    
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to perform alert action',
        details: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    );
  }
}






