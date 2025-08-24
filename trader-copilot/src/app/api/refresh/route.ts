import { NextRequest, NextResponse } from 'next/server';
import { verifyAuth } from '@/lib/auth';

export async function POST(request: NextRequest) {
  if (!verifyAuth(request)) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const fs = await import('fs/promises');
    const path = await import('path');
    
    // Create refresh request file for Python CLI to pick up
    const refreshFile = path.join(
      process.cwd(),
      '../data/runs/snapshots/refresh_request.json'
    );
    
    const refreshData = {
      type: 'manual_refresh',
      requested_at: new Date().toISOString(),
      requested_by: 'ui'
    };
    
    // Ensure directory exists
    await fs.mkdir(path.dirname(refreshFile), { recursive: true });
    
    // Write refresh request
    await fs.writeFile(refreshFile, JSON.stringify(refreshData, null, 2));
    
    console.log('Manual refresh request created:', refreshFile);
    
    return NextResponse.json(
      { message: 'Refresh triggered', timestamp: refreshData.requested_at },
      { status: 202 }
    );
  } catch (error) {
    console.error('Refresh API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}