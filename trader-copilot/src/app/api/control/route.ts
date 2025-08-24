import { NextRequest, NextResponse } from 'next/server';
import { verifyAuth } from '@/lib/auth';
import { promises as fs } from 'fs';
import path from 'path';

const controlFilePath = path.join(
  process.cwd(),
  '../data/runs/snapshots/polling_control.json'
);

// Helper function to read the control file
async function getPollingStatus() {
  try {
    await fs.access(controlFilePath); // Check if file exists
    const data = await fs.readFile(controlFilePath, 'utf-8');
    return JSON.parse(data);
  } catch (error) {
    // If file doesn't exist, default to disabled
    return { enabled: false, interval: 60 };
  }
}

// GET handler to check the current polling status
export async function GET(request: NextRequest) {
  if (!verifyAuth(request)) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const status = await getPollingStatus();
  return NextResponse.json(status);
}

// POST handler to enable or disable polling
export async function POST(request: NextRequest) {
  if (!verifyAuth(request)) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const { enabled, interval } = await request.json();

    if (typeof enabled !== 'boolean') {
      return NextResponse.json({ error: 'Invalid "enabled" value' }, { status: 400 });
    }

    const currentStatus = await getPollingStatus();
    const newStatus = {
      ...currentStatus,
      enabled,
      // Only update interval if provided, otherwise keep the existing one
      interval: typeof interval === 'number' ? interval : currentStatus.interval,
    };
    
    await fs.writeFile(controlFilePath, JSON.stringify(newStatus, null, 2));

    console.log(`Polling control updated: ${JSON.stringify(newStatus)}`);
    return NextResponse.json({ success: true, status: newStatus });

  } catch (error) {
    console.error('Failed to update polling control:', error);
    return NextResponse.json({ error: 'Failed to update polling status' }, { status: 500 });
  }
}
