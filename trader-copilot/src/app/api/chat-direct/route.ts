// Direct OpenAI API chat endpoint with streaming and tool calling
// Bypasses AI SDK to avoid compatibility issues

import { NextRequest, NextResponse } from 'next/server';
import { verifyAuth } from '@/lib/auth';
import { openaiTools, executeToolCall, buildSystemPrompt } from '@/lib/openai-direct';

const OPENAI_API_KEY = process.env.OPENAI_API_KEY;

// Model mapping for custom models
const MODEL_MAP: Record<string, string> = {
  'o3': 'o3',
  'o3-deep-research': 'o3-deep-research',
  'o4-mini-deep-research': 'o4-mini-deep-research',
  'gpt-5': 'gpt-5',
  'gpt-4': 'gpt-4-turbo-preview',
  'gpt-4o': 'gpt-4o',
  'gpt-4o-mini': 'gpt-4o-mini'
};

export async function POST(request: NextRequest) {
  if (!verifyAuth(request)) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const { messages, model = 'gpt-4o-mini' } = await request.json();
    
    const systemPrompt = await buildSystemPrompt();
    const actualModel = MODEL_MAP[model] || model;
    
    console.log(`Using model: ${actualModel}`);
    
    // Build the messages array with system prompt
    const allMessages = [
      { role: 'system', content: systemPrompt },
      ...messages
    ];

    // Create streaming response
    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      async start(controller) {
        try {
          await streamCompletion(controller, encoder, allMessages, actualModel);
        } catch (error) {
          console.error('Stream error:', error);
          controller.error(error);
        } finally {
          controller.close();
        }
      }
    });

    return new Response(stream, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      },
    });
  } catch (error) {
    console.error('Chat API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

async function streamCompletion(
  controller: ReadableStreamDefaultController,
  encoder: TextEncoder,
  messages: any[],
  model: string,
  maxSteps: number = 5
) {
  let currentMessages = [...messages];
  let stepCount = 0;

  while (stepCount < maxSteps) {
    stepCount++;
    
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${OPENAI_API_KEY}`,
      },
      body: JSON.stringify({
        model,
        messages: currentMessages,
        tools: openaiTools,
        tool_choice: 'auto',
        stream: true,
        // Note: o3, o3-deep-research, o4-mini-deep-research, gpt-5 only support default temperature
      }),
    });

    if (!response.ok) {
      const error = await response.text();
      console.error('OpenAI API error:', error);
      throw new Error(`OpenAI API error: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) throw new Error('No response body');

    const decoder = new TextDecoder();
    let buffer = '';
    let currentToolCalls: any[] = [];
    let accumulatedContent = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          if (data === '[DONE]') continue;

          try {
            const parsed = JSON.parse(data);
            const choice = parsed.choices?.[0];
            
            if (!choice) continue;
            
            const delta = choice.delta;
            
            // Handle regular content
            if (delta.content) {
              accumulatedContent += delta.content;
              // Stream the content to the client
              const clientData = JSON.stringify({
                type: 'content',
                content: delta.content
              });
              controller.enqueue(encoder.encode(`data: ${clientData}\n\n`));
            }
            
            // Handle tool calls
            if (delta.tool_calls) {
              for (const toolCall of delta.tool_calls) {
                const index = toolCall.index;
                
                // Initialize tool call if needed
                if (!currentToolCalls[index]) {
                  currentToolCalls[index] = {
                    id: toolCall.id || '',
                    type: 'function',
                    function: {
                      name: toolCall.function?.name || '',
                      arguments: ''
                    }
                  };
                }
                
                // Accumulate tool call data
                if (toolCall.id) {
                  currentToolCalls[index].id = toolCall.id;
                }
                if (toolCall.function?.name) {
                  currentToolCalls[index].function.name = toolCall.function.name;
                }
                if (toolCall.function?.arguments) {
                  currentToolCalls[index].function.arguments += toolCall.function.arguments;
                }
              }
            }
            
            // Check if this is the end of the response
            if (choice.finish_reason === 'tool_calls' && currentToolCalls.length > 0) {
              // Execute tool calls
              const toolResults = [];
              
              for (const toolCall of currentToolCalls) {
                const { name, arguments: argsStr } = toolCall.function;
                
                console.log(`Executing tool: ${name}`);
                
                let args = {};
                try {
                  args = argsStr ? JSON.parse(argsStr) : {};
                } catch (e) {
                  console.error(`Failed to parse tool arguments: ${argsStr}`);
                }
                
                const result = await executeToolCall(name, args);
                
                toolResults.push({
                  role: 'tool' as const,
                  tool_call_id: toolCall.id,
                  content: JSON.stringify(result)
                });
                
                // Notify client about tool execution
                const toolData = JSON.stringify({
                  type: 'tool_call',
                  name,
                  args,
                  result
                });
                controller.enqueue(encoder.encode(`data: ${toolData}\n\n`));
              }
              
              // Add assistant message with tool calls
              currentMessages.push({
                role: 'assistant',
                content: accumulatedContent || null,
                tool_calls: currentToolCalls
              });
              
              // Add tool results
              currentMessages.push(...toolResults);
              
              // Clear for next iteration
              currentToolCalls = [];
              accumulatedContent = '';
              
              // Continue to next step to get the final response
              break;
            }
            
            // If finished without tool calls, we're done
            if (choice.finish_reason === 'stop') {
              if (accumulatedContent) {
                currentMessages.push({
                  role: 'assistant',
                  content: accumulatedContent
                });
              }
              // Send completion signal
              controller.enqueue(encoder.encode('data: {"type":"done"}\n\n'));
              return;
            }
          } catch (e) {
            console.error('Error parsing SSE data:', e);
          }
        }
      }
    }
  }
  
  // If we've exhausted max steps, send a final message
  controller.enqueue(encoder.encode('data: {"type":"done"}\n\n'));
}