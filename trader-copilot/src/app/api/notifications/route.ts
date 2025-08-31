// API endpoint to retrieve system notifications

import { NextRequest, NextResponse } from 'next/server';
import { verifyAuth } from '@/lib/auth';
import { getAndClearNotifications } from '@/lib/openai-direct';

export async function GET(request: NextRequest) {
  if (!verifyAuth(request)) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const notifications = getAndClearNotifications();
    
    return NextResponse.json({ 
      notifications,
      count: notifications.length 
    });
  } catch (error) {
    console.error('Error retrieving notifications:', error);
    return NextResponse.json(
      { error: 'Failed to retrieve notifications' },
      { status: 500 }
    );
  }
}