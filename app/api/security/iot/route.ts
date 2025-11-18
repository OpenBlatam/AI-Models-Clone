import { NextRequest, NextResponse } from 'next/server';
import { iotSecurityManager } from '@/lib/security/iot-security';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const action = searchParams.get('action');

    switch (action) {
      case 'stats':
        const stats = await iotSecurityManager.getIoTStats();
        return NextResponse.json({ success: true, data: stats });

      default:
        return NextResponse.json({ error: 'Invalid action' }, { status: 400 });
    }
  } catch (error) {
    console.error('IoT Security API error:', error);
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
      case 'add_device':
        const device = await iotSecurityManager.addIoTDevice(data);
        return NextResponse.json({ success: true, data: device });

      case 'add_event':
        const event = await iotSecurityManager.addSecurityEvent(data);
        return NextResponse.json({ success: true, data: event });

      case 'schedule_update':
        const update = await iotSecurityManager.scheduleSecurityUpdate(data.deviceId, data.updateType, data.version, new Date(data.scheduledAt));
        return NextResponse.json({ success: true, data: update });

      case 'assess_device':
        const assessment = await iotSecurityManager.assessDeviceSecurity(data.deviceId);
        return NextResponse.json({ success: true, data: assessment });

      default:
        return NextResponse.json({ error: 'Invalid action' }, { status: 400 });
    }
  } catch (error) {
    console.error('IoT Security API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
