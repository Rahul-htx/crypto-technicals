import { z } from 'zod';
import { zodToJsonSchema } from 'zod-to-json-schema';
import { kv } from './kv';

// Define Zod schemas
const getSnapshotSchema = z.object({
  section: z.enum(['full', 'market', 'coin']).default('market').describe('Which section of the snapshot to return'),
  coin: z.string().optional().describe('Specific coin to get data for (required when section=coin)')
});

const updateThesisSchema = z.object({
  newThesis: z.string().min(10).describe('The new thesis content in markdown format')
});

// Convert Zod schemas to JSON Schema for OpenAI
const getSnapshotJsonSchema = zodToJsonSchema(getSnapshotSchema, {
  target: 'openApi3',
  $refStrategy: 'none'
});

const updateThesisJsonSchema = zodToJsonSchema(updateThesisSchema, {
  target: 'openApi3',
  $refStrategy: 'none'
});

// Define tools with proper JSON Schema format
export const getSnapshotTool = {
  type: 'function',
  function: {
    name: 'getSnapshot',
    description: 'Fetches the latest market snapshot. Use section="coin" when you only need data for a single ticker. Default returns market_overview to minimize tokens.',
    parameters: getSnapshotJsonSchema,
    execute: async ({ section = 'market', coin }: z.infer<typeof getSnapshotSchema>) => {
      const { json } = await kv.load();
      
      if (!json) {
        return { error: 'snapshot unavailable' };
      }

      switch (section) {
        case 'full':
          return json;
        
        case 'market':
          // Extract market overview from all horizons present
          const marketData: any = {};
          
          for (const horizon of json.meta.horizons_present || []) {
            if (json[horizon]?.market_overview) {
              marketData[horizon] = json[horizon].market_overview;
            }
          }
          
          return {
            meta: json.meta,
            market_data: marketData
          };
        
        case 'coin':
          if (!coin) {
            throw new Error('coin required for section="coin"');
          }
          
          const coinLower = coin.toLowerCase();
          const coinData: any = {};
          
          for (const horizon of json.meta.horizons_present || []) {
            if (json[horizon]?.coins?.[coinLower]) {
              coinData[horizon] = json[horizon].coins[coinLower];
            }
          }
          
          if (Object.keys(coinData).length === 0) {
            return { error: `coin ${coin} not found` };
          }
          
          return {
            coin: coinLower,
            data: coinData
          };
        
        default:
          return json.meta || { error: 'no meta data available' };
      }
    }
  }
};

export const updateThesisTool = {
  type: 'function',
  function: {
    name: 'updateThesis',
    description: 'Overwrite the current investment thesis markdown. Use this when the user asks to update their trading thesis or when market conditions require thesis adjustments.',
    parameters: updateThesisJsonSchema,
    execute: async ({ newThesis }: z.infer<typeof updateThesisSchema>) => {
      // This tool execution happens server-side, so we need to use the thesis API directly
      try {
        const fs = await import('fs/promises');
        const path = await import('path');
        
        const THESIS_FILE = path.join(process.cwd(), 'data', 'thesis.json');
        const thesisData = {
          thesis: newThesis,
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
  }
};

export const tools = {
  getSnapshot: getSnapshotTool.function,
  updateThesis: updateThesisTool.function
};