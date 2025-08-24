import { NextRequest, NextResponse } from 'next/server';
import { verifyAuth } from '@/lib/auth';
import { promises as fs } from 'fs';
import path from 'path';

interface UpdateSignal {
  type: string;
  timestamp: string;
  hash: string;
  at: string;
}

// In-memory cache for the signal
let lastSignal: UpdateSignal | null = null;
let lastReadTime = 0;

export async function GET(request: NextRequest) {
  if (!verifyAuth(request)) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const now = Date.now();
    // Cache check to reduce disk I/O
    if (now - lastReadTime < 1000 && lastSignal) {
      return NextResponse.json(lastSignal);
    }

    const signalPath = path.join(
      process.cwd(),
      '../data/runs/snapshots/update_signal.json'
    );
    
    const data = await fs.readFile(signalPath, 'utf-8');
    const signal = JSON.parse(data) as UpdateSignal;

    lastSignal = signal;
    lastReadTime = now;
    
    return NextResponse.json(signal);
  } catch (error) {
    // If the file doesn't exist or is invalid, return the last known signal or a default
    if (lastSignal) {
      return NextResponse.json(lastSignal);
    }
    return NextResponse.json({ hash: 'no-signal' }, { status: 404 });
  }
}
