import { NextRequest, NextResponse } from 'next/server';
import { verifyAuth } from '@/lib/auth';
import { 
  loadRecent, 
  loadContext,
  appendMessage, 
  getStats, 
  clearCurrentMonth,
  type ChatMessage 
} from '@/lib/chat-store';

// GET: Load chat history with multiple modes
export async function GET(request: NextRequest) {
  if (!verifyAuth(request)) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const { searchParams } = new URL(request.url);
    const mode = searchParams.get('mode') || 'context';
    const includeStats = searchParams.get('stats') === 'true';
    
    let messages: ChatMessage[] = [];
    
    switch (mode) {
      case 'context':
        // New default: multi-month context-aware loading
        const budgetOverride = searchParams.get('limitTokens') 
          ? parseInt(searchParams.get('limitTokens')!) 
          : undefined;
        messages = await loadContext(budgetOverride);
        break;
        
      case 'recent':
        // Legacy mode: single month with token limit
        const limitTokens = parseInt(searchParams.get('limitTokens') || '200000');
        messages = await loadRecent(limitTokens);
        break;
        
      case 'stats':
        // Stats-only mode
        const stats = await getStats();
        return NextResponse.json({ stats });
        
      default:
        return NextResponse.json(
          { error: `Invalid mode: ${mode}. Use 'context', 'recent', or 'stats'` },
          { status: 400 }
        );
    }
    
    const response: any = { messages, mode };
    
    if (includeStats) {
      response.stats = await getStats();
    }
    
    return NextResponse.json(response);
  } catch (error) {
    console.error('Failed to load chat history:', error);
    return NextResponse.json(
      { error: 'Failed to load chat history' },
      { status: 500 }
    );
  }
}

// POST: Append a message to chat history
export async function POST(request: NextRequest) {
  if (!verifyAuth(request)) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const body = await request.json();
    
    // Validate required fields
    if (!body.role || !body.content) {
      return NextResponse.json(
        { error: 'Missing required fields: role and content' },
        { status: 400 }
      );
    }
    
    // Append the message
    const message = await appendMessage({
      role: body.role,
      content: body.content,
      model: body.model,
      toolCalls: body.toolCalls,
      metadata: body.metadata
    });
    
    return NextResponse.json({ 
      success: true, 
      message 
    });
  } catch (error) {
    console.error('Failed to append message:', error);
    return NextResponse.json(
      { error: 'Failed to save message' },
      { status: 500 }
    );
  }
}

// DELETE: Clear current month's history (for testing/reset)
export async function DELETE(request: NextRequest) {
  if (!verifyAuth(request)) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    await clearCurrentMonth();
    return NextResponse.json({ 
      success: true, 
      message: 'Chat history cleared for current month' 
    });
  } catch (error) {
    console.error('Failed to clear chat history:', error);
    return NextResponse.json(
      { error: 'Failed to clear chat history' },
      { status: 500 }
    );
  }
}