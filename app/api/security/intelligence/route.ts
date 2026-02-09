import { NextRequest, NextResponse } from 'next/server';
import { advancedSecurityIntelligenceManager } from '@/lib/security/advanced-security-intelligence';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const action = searchParams.get('action');

    switch (action) {
      case 'stats':
        const stats = await advancedSecurityIntelligenceManager.getIntelligenceStats();
        return NextResponse.json({ success: true, data: stats });

      case 'search':
        const query = {
          type: searchParams.get('type') || undefined,
          severity: searchParams.get('severity') || undefined,
          tags: searchParams.get('tags')?.split(',') || undefined,
          source: searchParams.get('source') || undefined,
          limit: parseInt(searchParams.get('limit') || '100'),
        };
        const results = await advancedSecurityIntelligenceManager.searchThreatIntelligence(query);
        return NextResponse.json({ success: true, data: results });

      default:
        return NextResponse.json({ error: 'Invalid action' }, { status: 400 });
    }
  } catch (error) {
    console.error('Intelligence API error:', error);
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
      case 'add_intelligence':
        const intelligence = await advancedSecurityIntelligenceManager.addThreatIntelligence(data);
        return NextResponse.json({ success: true, data: intelligence });

      case 'add_source':
        const source = await advancedSecurityIntelligenceManager.addThreatSource(data);
        return NextResponse.json({ success: true, data: source });

      case 'create_hunt':
        const hunt = await advancedSecurityIntelligenceManager.createThreatHunt(data);
        return NextResponse.json({ success: true, data: hunt });

      case 'execute_hunt':
        const huntResults = await advancedSecurityIntelligenceManager.executeThreatHunt(data.huntId);
        return NextResponse.json({ success: true, data: huntResults });

      case 'analyze':
        const analysis = await advancedSecurityIntelligenceManager.analyzeThreatIntelligence(data.intelligenceId);
        return NextResponse.json({ success: true, data: analysis });

      default:
        return NextResponse.json({ error: 'Invalid action' }, { status: 400 });
    }
  } catch (error) {
    console.error('Intelligence API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
