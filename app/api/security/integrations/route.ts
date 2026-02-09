/**
 * Security Integrations API Routes
 * Manage external security service integrations
 */

import { NextRequest, NextResponse } from 'next/server';
import { securityIntegrationsManager } from '@/lib/security';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const type = searchParams.get('type');
    const status = searchParams.get('status');

    let integrations = securityIntegrationsManager.getAllIntegrations();

    if (type) {
      integrations = integrations.filter(integration => integration.type === type);
    }

    if (status) {
      integrations = integrations.filter(integration => integration.status === status);
    }

    return NextResponse.json({
      integrations,
      stats: securityIntegrationsManager.getIntegrationStats(),
    });
  } catch (error) {
    console.error('Failed to get integrations:', error);
    return NextResponse.json(
      { error: 'Failed to get integrations' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { action, integration } = body;

    switch (action) {
      case 'add':
        securityIntegrationsManager.addIntegration(integration);
        return NextResponse.json({ message: 'Integration added successfully' });

      case 'update':
        const updated = securityIntegrationsManager.updateIntegration(integration.id, integration);
        if (!updated) {
          return NextResponse.json(
            { error: 'Integration not found' },
            { status: 404 }
          );
        }
        return NextResponse.json({ message: 'Integration updated successfully' });

      case 'remove':
        const removed = securityIntegrationsManager.removeIntegration(integration.id);
        if (!removed) {
          return NextResponse.json(
            { error: 'Integration not found' },
            { status: 404 }
          );
        }
        return NextResponse.json({ message: 'Integration removed successfully' });

      case 'test':
        const testResult = await securityIntegrationsManager.testIntegration(integration.id);
        return NextResponse.json(testResult);

      case 'send-notification':
        const sent = await securityIntegrationsManager.sendResponseNotification(
          integration.id,
          integration.alert
        );
        return NextResponse.json({ success: sent });

      default:
        return NextResponse.json(
          { error: 'Invalid action' },
          { status: 400 }
        );
    }
  } catch (error) {
    console.error('Failed to process integration request:', error);
    return NextResponse.json(
      { error: 'Failed to process integration request' },
      { status: 500 }
    );
  }
}
