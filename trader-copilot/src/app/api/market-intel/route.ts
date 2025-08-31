import { NextRequest, NextResponse } from 'next/server';
import { verifyAuth } from '@/lib/auth';
import fs from 'fs/promises';
import path from 'path';

const MARKET_INTEL_FILE = path.join(process.cwd(), 'data', 'market_intel.json');

export async function GET(request: NextRequest) {
  if (!verifyAuth(request)) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const data = await fs.readFile(MARKET_INTEL_FILE, 'utf-8');
    const marketIntel = JSON.parse(data);
    return NextResponse.json(marketIntel);
  } catch (error: any) {
    console.error('Failed to load market intelligence:', error);
    
    if (error.code === 'ENOENT') {
      return NextResponse.json({ 
        error: 'Market intelligence file not found',
        version: 2,
        last_updated: new Date().toISOString(),
        updated_by: 'system',
        core: { last_verified: new Date().toISOString(), items: [] },
        diff: { items: [] },
        metadata: { core_token_count: 0, diff_token_count: 0, total_token_count: 0 }
      });
    }
    
    return NextResponse.json(
      { error: 'Failed to load market intelligence' },
      { status: 500 }
    );
  }
}