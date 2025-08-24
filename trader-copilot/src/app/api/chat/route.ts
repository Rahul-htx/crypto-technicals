import { openai } from '@ai-sdk/openai';
import { streamText } from 'ai';
import { NextRequest, NextResponse } from 'next/server';
import { verifyAuth } from '@/lib/auth';
import { tools } from '@/lib/tools';

// System prompt function that doesn't include snapshot data
async function buildSystemPrompt(): Promise<string> {
  try {
    // Load current thesis for system context
    const fs = await import('fs/promises');
    const path = await import('path');
    
    const THESIS_FILE = path.join(process.cwd(), 'data', 'thesis.json');
    
    let thesisSection = '# Investment Thesis\n*No thesis available - use updateThesis tool to set one*';
    
    try {
      const data = await fs.readFile(THESIS_FILE, 'utf-8');
      const thesisData = JSON.parse(data);
      thesisSection = `# Investment Thesis
Last updated: ${thesisData.updatedAt} by ${thesisData.updatedBy}

${thesisData.thesis}`;
    } catch {
      // Use default thesis section
    }

    return `You are Trader Copilot, an AI assistant specialized in cryptocurrency trading and market analysis.

${thesisSection}

## Your Role
- Provide trading insights based on the current investment thesis and live market data
- Use the getSnapshot tool to access current market data when needed
- Help users analyze market conditions and identify trading opportunities
- Update the thesis when market conditions change significantly
- Be concise and actionable in your responses

## Key Principles
- Always use getSnapshot with section='market' by default to minimize tokens
- Only request section='full' when you need comprehensive analysis
- Use section='coin' with a specific coin when focusing on individual assets
- Keep responses focused on trading insights rather than general market commentary
- Reference specific data points from snapshots to support your analysis

## Available Tools
- getSnapshot: Access latest market data (default: market overview only)
- updateThesis: Modify the investment thesis when conditions warrant changes

Start by asking what the user wants to analyze or if they need help with their current positions.`;
  } catch (error) {
    console.error('Error building system prompt:', error);
    return 'You are Trader Copilot, a cryptocurrency trading assistant. Use the getSnapshot tool to access market data and help with trading decisions.';
  }
}

export async function POST(request: NextRequest) {
  if (!verifyAuth(request)) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const { messages, model = 'o3' } = await request.json();

    const systemPrompt = await buildSystemPrompt();
    
    // Organization is now verified, use proper models with tools re-enabled
    const result = await streamText({
      model: openai(model),
      messages,
      system: systemPrompt,
      tools,
      maxSteps: 5,
    });

    return result.toTextStreamResponse();
  } catch (error) {
    console.error('Chat API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}