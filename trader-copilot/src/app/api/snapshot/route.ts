import { NextRequest, NextResponse } from 'next/server';
import { kv } from '@/lib/kv';
import { verifyAuth } from '@/lib/auth';

export async function GET(request: NextRequest) {
  if (!verifyAuth(request)) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const snapshot = await kv.load();
    
    if (!snapshot.json) {
      return NextResponse.json(
        { error: 'Snapshot not available' },
        { status: 503 }
      );
    }

    return NextResponse.json(snapshot.json);
  } catch (error) {
    console.error('Snapshot API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}