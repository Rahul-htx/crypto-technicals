import { openai } from '@ai-sdk/openai';
import { streamText } from 'ai';
import { z } from 'zod';
import { tool } from 'ai';
import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

// A dead-simple tool for testing
const testTools = {
  add: tool({
    description: 'Adds two numbers',
    parameters: z.object({
      a: z.number(),
      b: z.number(),
    }),
    execute: async ({ a, b }) => a + b,
  }),
};

export async function POST(request: NextRequest) {
  try {
    const { messages } = await request.json();

    const result = await streamText({
      model: openai('gpt-4o-mini'), // Hardcode a known-good model
      messages,
      tools: testTools,
    });

    return result.toTextStreamResponse();
  } catch (error: any) {
    console.error('Minimal test chat API error:', error);
    return NextResponse.json(
      { error: 'Internal server error', details: error.message },
      { status: 500 }
    );
  }
}
