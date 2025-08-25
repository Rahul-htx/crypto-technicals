import { NextRequest, NextResponse } from 'next/server';
import { verifyAuth } from '@/lib/auth';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export async function POST(request: NextRequest) {
  if (!verifyAuth(request)) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const refreshData = {
      type: 'manual_refresh',
      requested_at: new Date().toISOString(),
      requested_by: 'ui'
    };
    
    console.log('🔄 Manual refresh triggered at:', refreshData.requested_at);
    
    // Directly execute Python CLI to generate fresh snapshot
    const pythonCmd = process.env.PYTHON_CMD || 'python';
    const { stdout, stderr } = await execAsync(
      `cd .. && source venv/bin/activate && ${pythonCmd} -m src.cli --verbose`,
      { 
        timeout: 60000, // 60 second timeout
        env: { ...process.env, FORCE_REFRESH: 'true' }
      }
    );
    
    if (stderr) {
      console.warn('Python CLI stderr:', stderr);
    }
    
    console.log('✅ Python CLI completed successfully');
    console.log('📊 Fresh snapshot generated');
    
    return NextResponse.json(
      { 
        message: 'Refresh completed', 
        timestamp: refreshData.requested_at,
        status: 'success'
      },
      { status: 200 }
    );
  } catch (error: any) {
    console.error('❌ Refresh failed:', error);
    
    return NextResponse.json(
      { 
        error: 'Refresh failed',
        message: error.message || 'Unknown error',
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    );
  }
}