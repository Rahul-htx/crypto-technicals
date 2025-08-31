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
  },
  {
    type: "function" as const,
    function: {
      name: "get_market_intel",
      description: "Get full market intelligence including all core facts, diff items, and metadata.",
      parameters: {
        type: "object",
        properties: {
          include_archived: {
            type: "boolean",
            description: "Include archived/historical entries from vector DB"
          }
        },
        required: [],
        additionalProperties: false
      }
    }
  },
  {
    type: "function" as const,
    function: {
      name: "update_market_intel",
      description: "Add to diff, promote to core, or perform maintenance on market intelligence.",
      parameters: {
        type: "object",
        properties: {
          action: {
            type: "string",
            enum: ["add_diff", "promote_to_core", "prune_stale", "run_curation"],
            description: "Action to perform on market intelligence"
          },
          payload: {
            type: "object",
            properties: {
              content: {
                type: "string",
                description: "New market event or update (for add_diff)"
              },
              confidence: {
                type: "number",
                minimum: 0,
                maximum: 1,
                description: "Confidence score for the update"
              },
              source: {
                type: "string",
                description: "Source URL or reference for the update"
              },
              diff_id: {
                type: "string",
                description: "ID of diff item to promote (for promote_to_core)"
              },
              category: {
                type: "string",
                enum: ["regulatory", "principle", "market_structure", "macro"],
                description: "Category for core item (for promote_to_core)"
              },
              days_threshold: {
                type: "number",
                description: "Days threshold for pruning stale items"
              }
            }
          }
        },
        required: ["action", "payload"],
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
    
    case 'get_market_intel': {
      try {
        const fs = await import('fs/promises');
        const path = await import('path');
        const MARKET_INTEL_FILE = path.join(process.cwd(), 'data', 'market_intel.json');
        
        const data = await fs.readFile(MARKET_INTEL_FILE, 'utf-8');
        const marketIntel = JSON.parse(data);
        
        // Always return the full structured data
        const response = {
          version: marketIntel.version,
          last_updated: marketIntel.last_updated,
          core: marketIntel.core,
          diff: marketIntel.diff,
          metadata: marketIntel.metadata
        };
        
        // Optionally include archived items from vector DB
        if (args.include_archived) {
          // TODO: Query vector DB for historical items
          response.archived = [];
        }
        
        return response;
      } catch (error) {
        return { error: 'Failed to load market intelligence', details: error.message };
      }
    }
    
    case 'update_market_intel': {
      try {
        const fs = await import('fs/promises');
        const path = await import('path');
        const lockfile = require('proper-lockfile');
        const MARKET_INTEL_FILE = path.join(process.cwd(), 'data', 'market_intel.json');
        const HISTORY_DIR = path.join(process.cwd(), 'data', 'market_intel_history');
        
        // Implement file locking
        const release = await lockfile.lock(MARKET_INTEL_FILE, { retries: 3, minTimeout: 100 });
        
        try {
          // Load current state
          const data = await fs.readFile(MARKET_INTEL_FILE, 'utf-8');
          const marketIntel = JSON.parse(data);
          
          // Save history snapshot
          const timestamp = new Date().toISOString();
          await fs.mkdir(HISTORY_DIR, { recursive: true });
          await fs.writeFile(
            path.join(HISTORY_DIR, `${timestamp.replace(/[:.]/g, '-')}.json`),
            JSON.stringify(marketIntel, null, 2)
          );
          
          // Perform the requested action
          switch (args.action) {
            case 'add_diff':
              if (!args.payload.content) {
                return { success: false, error: 'Content required for add_diff action' };
              }
              const newDiffId = `diff-${Date.now()}`;
              marketIntel.diff.items.push({
                id: newDiffId,
                content: args.payload.content,
                created_at: timestamp,
                hit_count: 0,
                confidence: args.payload.confidence || 0.8,
                promotion_eligible: false,
                source: args.payload.source || ''
              });
              break;
              
            case 'promote_to_core':
              if (!args.payload.diff_id) {
                return { success: false, error: 'diff_id required for promote_to_core action' };
              }
              const diffItem = marketIntel.diff.items.find(i => i.id === args.payload.diff_id);
              if (diffItem) {
                const newCoreId = `core-${Date.now()}`;
                marketIntel.core.items.push({
                  id: newCoreId,
                  content: diffItem.content,
                  category: args.payload.category || 'principle',
                  last_verified: timestamp,
                  reference_count: 0
                });
                // Remove from diff
                marketIntel.diff.items = marketIntel.diff.items.filter(i => i.id !== args.payload.diff_id);
              } else {
                return { success: false, error: `Diff item ${args.payload.diff_id} not found` };
              }
              break;
              
            case 'prune_stale':
              const threshold = new Date();
              threshold.setDate(threshold.getDate() - (args.payload.days_threshold || 30));
              const originalCount = marketIntel.core.items.length;
              marketIntel.core.items = marketIntel.core.items.filter(
                item => new Date(item.last_verified) > threshold || item.reference_count > 5
              );
              const prunedCount = originalCount - marketIntel.core.items.length;
              break;
              
            case 'run_curation':
              // This would call gpt-5-mini to analyze and suggest promotions
              // Implementation deferred to actual curation service
              return { message: 'Curation service not yet implemented' };
              
            default:
              return { success: false, error: `Unknown action: ${args.action}` };
          }
          
          // Update metadata
          marketIntel.last_updated = timestamp;
          marketIntel.updated_by = 'ai-agent';
          
          // Recalculate token counts (using simple estimation)
          const coreText = marketIntel.core.items.map(i => i.content).join(' ');
          const diffText = marketIntel.diff.items.map(i => i.content).join(' ');
          
          // Simple token estimation: roughly 1 token per 4 characters
          marketIntel.metadata.core_token_count = Math.ceil(coreText.length / 4);
          marketIntel.metadata.diff_token_count = Math.ceil(diffText.length / 4);
          marketIntel.metadata.total_token_count = 
            marketIntel.metadata.core_token_count + marketIntel.metadata.diff_token_count;
          
          // Validate against schema (optional - can skip for now)
          // const Ajv = require('ajv');
          // const schema = require('../specs/market_intel.schema.json');
          // const ajv = new Ajv();
          // const validate = ajv.compile(schema);
          // 
          // if (!validate(marketIntel)) {
          //   throw new Error(`Schema validation failed: ${JSON.stringify(validate.errors)}`);
          // }
          
          // Write updated file
          await fs.writeFile(MARKET_INTEL_FILE, JSON.stringify(marketIntel, null, 2));
          
          return {
            success: true,
            action: args.action,
            token_usage: marketIntel.metadata.total_token_count,
            timestamp,
            details: args.action === 'prune_stale' ? { pruned_items: prunedCount } : undefined
          };
          
        } finally {
          // Always release the lock
          await release();
        }
      } catch (error) {
        console.error('Failed to update market intelligence:', error);
        return { success: false, error: 'Failed to update market intelligence', details: error.message };
      }
    }
    
    case 'web_search_preview':
      // OpenAI handles this tool natively, we shouldn't receive it in executeToolCall
      // but handle it gracefully just in case
      return { note: 'Web search handled by OpenAI' };
    
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
    const MARKET_INTEL_FILE = path.join(process.cwd(), 'data', 'market_intel.json');
    
    // Load thesis (existing code)
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
    
    // Load market intelligence summary (NEW)
    let marketIntelSection = '';
    try {
      const data = await fs.readFile(MARKET_INTEL_FILE, 'utf-8');
      const marketIntel = JSON.parse(data);
      
      // Build core summary
      const coreItems = marketIntel.core.items
        .map(item => `• ${item.content}`)
        .join('\n');
      
      // Build diff summary
      const diffItems = marketIntel.diff.items
        .map(item => `• ${item.content}`)
        .join('\n');
      
      marketIntelSection = `

# Market Intelligence
Last updated: ${marketIntel.last_updated}

## Core Facts (Stable)
${coreItems}

## Recent Updates (Diff)
${diffItems}

Token usage: ${marketIntel.metadata.total_token_count} / 10,000
For full historical context, use the \`get_market_intel\` tool.`;
    } catch {
      marketIntelSection = '\n\n# Market Intelligence\nNo market intelligence available. Use `update_market_intel` to add current events.';
    }

    return `You are Trader Copilot, an AI assistant specialized in cryptocurrency trading and market analysis.

${thesisSection}

${marketIntelSection}

## Your Role
- Provide trading insights based on the investment thesis, market intelligence, and live data
- Consider recent news and regulatory changes when making recommendations
- Use tools to access detailed information when needed
- Be concise and actionable in your responses

## Key Principles
- Always consider the market intelligence summary in your analysis
- Use get_market_intel for detailed news context when relevant
- Keep responses focused on actionable trading insights
- Update market intelligence when you encounter significant new information
- Always use get_market_snapshot by default to minimize tokens
- Only use get_full_snapshot when you need comprehensive analysis
- Use get_coin_snapshot when focusing on individual assets

## Available Tools
- get_market_snapshot: Access market overview data
- get_coin_snapshot: Get data for a specific coin
- get_full_snapshot: Get complete snapshot (use sparingly)
- get_market_intel: Access detailed news and trading principles
- update_thesis: Modify the investment thesis
- update_market_intel: Add or update market intelligence

When asked about prices or market data, always use the appropriate tool to get real-time information.`;
  } catch (error) {
    console.error('Error building system prompt:', error);
    return 'You are Trader Copilot, a cryptocurrency trading assistant. Use the available tools to access market data and help with trading decisions.';
  }
}