import { NextRequest, NextResponse } from 'next/server';
import { advancedSecurityForensicsManager } from '@/lib/security/advanced-security-forensics';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const action = searchParams.get('action');

    switch (action) {
      case 'stats':
        const stats = await advancedSecurityForensicsManager.getForensicsStats();
        return NextResponse.json({ success: true, data: stats });

      case 'evidence':
        const evidenceId = searchParams.get('id');
        if (!evidenceId) {
          return NextResponse.json({ error: 'Evidence ID required' }, { status: 400 });
        }
        const evidence = await advancedSecurityForensicsManager.getDigitalEvidence(evidenceId);
        return NextResponse.json({ success: true, data: evidence });

      case 'incident':
        const incidentId = searchParams.get('id');
        if (!incidentId) {
          return NextResponse.json({ error: 'Incident ID required' }, { status: 400 });
        }
        const incident = await advancedSecurityForensicsManager.getSecurityIncident(incidentId);
        return NextResponse.json({ success: true, data: incident });

      default:
        return NextResponse.json({ error: 'Invalid action' }, { status: 400 });
    }
  } catch (error) {
    console.error('Forensics API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { action, data } = body;

    switch (action) {
      case 'add_evidence':
        const evidence = await advancedSecurityForensicsManager.addDigitalEvidence(data);
        return NextResponse.json({ success: true, data: evidence });

      case 'create_incident':
        const incident = await advancedSecurityForensicsManager.createSecurityIncident(data);
        return NextResponse.json({ success: true, data: incident });

      case 'update_incident_status':
        const updatedIncident = await advancedSecurityForensicsManager.updateIncidentStatus(data.incidentId, data.status);
        return NextResponse.json({ success: true, data: updatedIncident });

      case 'add_incident_action':
        const action_result = await advancedSecurityForensicsManager.addIncidentAction(data.incidentId, data.action);
        return NextResponse.json({ success: true, data: action_result });

      case 'create_analysis':
        const analysis = await advancedSecurityForensicsManager.createForensicAnalysis(data);
        return NextResponse.json({ success: true, data: analysis });

      case 'generate_report':
        const report = await advancedSecurityForensicsManager.generateForensicReport(data.analysisId);
        return NextResponse.json({ success: true, data: report });

      default:
        return NextResponse.json({ error: 'Invalid action' }, { status: 400 });
    }
  } catch (error) {
    console.error('Forensics API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
