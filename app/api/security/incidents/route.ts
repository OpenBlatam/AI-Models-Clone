import { NextRequest, NextResponse } from 'next/server';
import { securityIncidentResponseManager } from '@/lib/security/security-incident-response';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const status = searchParams.get('status');
    const severity = searchParams.get('severity');
    const category = searchParams.get('category');
    const assignedTo = searchParams.get('assignedTo');
    const limit = parseInt(searchParams.get('limit') || '50');

    // Get incidents with filters
    const incidents = securityIncidentResponseManager.getIncidents({
      status: status as any,
      severity: severity as any,
      category: category as any,
      assignedTo: assignedTo || undefined,
    });

    // Limit results
    const limitedIncidents = incidents.slice(0, limit);

    // Get statistics
    const statistics = securityIncidentResponseManager.getIncidentStatistics();

    return NextResponse.json({
      success: true,
      data: {
        incidents: limitedIncidents,
        total: incidents.length,
        statistics,
        filters: { status, severity, category, assignedTo, limit },
        generated_at: new Date().toISOString(),
      },
      timestamp: new Date().toISOString(),
    });

  } catch (error) {
    console.error('Security incidents error:', error);
    
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to get security incidents',
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
    const { title, description, severity, category, priority, source, affectedSystems, affectedUsers, estimatedImpact, metadata } = body;

    // Validate required fields
    if (!title || !description || !severity || !category) {
      return NextResponse.json(
        {
          success: false,
          error: 'Missing required fields: title, description, severity, category',
          timestamp: new Date().toISOString(),
        },
        { status: 400 }
      );
    }

    // Create incident
    const incident = await securityIncidentResponseManager.createIncident({
      title,
      description,
      severity,
      category,
      priority,
      source,
      affectedSystems,
      affectedUsers,
      estimatedImpact,
      metadata,
    });

    return NextResponse.json({
      success: true,
      data: {
        incident,
        message: 'Security incident created successfully',
      },
      timestamp: new Date().toISOString(),
    });

  } catch (error) {
    console.error('Security incident creation error:', error);
    
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to create security incident',
        details: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    );
  }
}