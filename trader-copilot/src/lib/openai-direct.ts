// Direct OpenAI API implementation without AI SDK
// Maintains dual-channel memory architecture

import { kv } from './kv';

// Tool definitions in OpenAI format (snake_case, strict schemas)
export const openaiTools = [
  {
    type: "function" as const,
    function: {
      name: "get_market_snapshot",
      description: "Fetches the high-level market overview data from the latest snapshot.",
      parameters: {
        type: "object",
        properties: {},
        required: [],
        additionalProperties: false
      }
    }
  },
  {
    type: "function" as const,
    function: {
      name: "get_coin_snapshot",
      description: "Fetches all available data for a single specified coin from the latest snapshot.",
      parameters: {
        type: "object",
        properties: {
          coin: {
            type: "string",
            description: "The coin's symbol, e.g., 'ethereum' or 'bitcoin'"
          }
        },
        required: ["coin"],
        additionalProperties: false
      }
    }
  },
  {
    type: "function" as const,
    function: {
      name: "get_full_snapshot",
      description: "Fetches the entire, raw market snapshot. Warning: This is a large amount of data.",
      parameters: {
        type: "object",
        properties: {},
        required: [],
        additionalProperties: false
      }
    }
  },
  {
    type: "function" as const,
    function: {
      name: "update_thesis",
      description: "Overwrites the current investment thesis markdown.",
      parameters: {
        type: "object",
        properties: {
          new_thesis: {
            type: "string",
            description: "The new thesis content in markdown format (minimum 10 characters)."
          }
        },
        required: ["new_thesis"],
        additionalProperties: false
      }
    }
  }
];

// Tool execution functions (maintaining dual-channel memory)
export async function executeToolCall(name: string, args: any): Promise<any> {
  switch (name) {
    case 'get_market_snapshot': {
      const { json } = await kv.load();
      if (!json) return { error: 'snapshot unavailable' };
      const marketData: any = {};
      for (const horizon of json.meta?.horizons_present || []) {
        if (json[horizon]?.market_overview) {
          marketData[horizon] = json[horizon].market_overview;
        }
      }
      return { meta: json.meta, market_data: marketData };
    }
    
    case 'get_coin_snapshot': {
      const { json } = await kv.load();
      if (!json) return { error: 'snapshot unavailable' };
      
      const coinLower = args.coin?.toLowerCase();
      if (!coinLower) return { error: 'coin parameter required' };
      
      const coinData: any = {};
      for (const horizon of json.meta?.horizons_present || []) {
        if (json[horizon]?.coins?.[coinLower]) {
          coinData[horizon] = json[horizon].coins[coinLower];
        }
      }
      if (Object.keys(coinData).length === 0) {
        return { error: `coin ${args.coin} not found` };
      }
      return { coin: coinLower, data: coinData };
    }
    
    case 'get_full_snapshot': {
      const { json } = await kv.load();
      return json || { error: 'snapshot unavailable' };
    }
    
    case 'update_thesis': {
      try {
        const fs = await import('fs/promises');
        const path = await import('path');
        const THESIS_FILE = path.join(process.cwd(), 'data', 'thesis.json');
        
        if (!args.new_thesis || args.new_thesis.length < 10) {
          return { success: false, error: 'Thesis must be at least 10 characters' };
        }
        
        const thesisData = {
          thesis: args.new_thesis,
          updatedAt: new Date().toISOString(),
          updatedBy: 'ai-assistant'
        };
        
        await fs.mkdir(path.dirname(THESIS_FILE), { recursive: true });
        await fs.writeFile(THESIS_FILE, JSON.stringify(thesisData, null, 2));
        return { success: true, message: 'Thesis updated successfully' };
      } catch (error) {
        console.error('Failed to update thesis:', error);
        return { success: false, error: 'Failed to update thesis' };
      }
    }
    
    default:
      return { error: `Unknown tool: ${name}` };
  }
}

// Build system prompt (dual-channel: thesis in prompt, snapshot via tools)
export async function buildSystemPrompt(): Promise<string> {
  try {
    const fs = await import('fs/promises');
    const path = await import('path');
    
    const THESIS_FILE = path.join(process.cwd(), 'data', 'thesis.json');
    
    let thesisSection = '# Investment Thesis\n*No thesis available - use update_thesis tool to set one*';
    
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
- Use the get_market_snapshot, get_coin_snapshot, or get_full_snapshot tools to access current market data
- Help users analyze market conditions and identify trading opportunities
- Update the thesis when market conditions change significantly
- Be concise and actionable in your responses

## Key Principles
- Always use get_market_snapshot by default to minimize tokens
- Only use get_full_snapshot when you need comprehensive analysis
- Use get_coin_snapshot when focusing on individual assets
- Keep responses focused on trading insights rather than general market commentary
- Reference specific data points from snapshots to support your analysis

## Available Tools
- get_market_snapshot: Access market overview data
- get_coin_snapshot: Get data for a specific coin
- get_full_snapshot: Get complete snapshot (use sparingly)
- update_thesis: Modify the investment thesis

When asked about prices or market data, always use the appropriate tool to get real-time information.`;
  } catch (error) {
    console.error('Error building system prompt:', error);
    return 'You are Trader Copilot, a cryptocurrency trading assistant. Use the available tools to access market data and help with trading decisions.';
  }
}