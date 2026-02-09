import { NextRequest, NextResponse } from 'next/server';
import { blockchainSecurityManager } from '@/lib/security/blockchain-security';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const action = searchParams.get('action');

    switch (action) {
      case 'stats':
        const stats = await blockchainSecurityManager.getBlockchainStats();
        return NextResponse.json({ success: true, data: stats });

      default:
        return NextResponse.json({ error: 'Invalid action' }, { status: 400 });
    }
  } catch (error) {
    console.error('Blockchain Security API error:', error);
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
      case 'add_node':
        const node = await blockchainSecurityManager.addBlockchainNode(data);
        return NextResponse.json({ success: true, data: node });

      case 'add_transaction':
        const transaction = await blockchainSecurityManager.addSecurityTransaction(data);
        return NextResponse.json({ success: true, data: transaction });

      case 'audit_contract':
        const audit = await blockchainSecurityManager.auditSmartContract(data.contractAddress, data.contractName, data.blockchain);
        return NextResponse.json({ success: true, data: audit });

      default:
        return NextResponse.json({ error: 'Invalid action' }, { status: 400 });
    }
  } catch (error) {
    console.error('Blockchain Security API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}