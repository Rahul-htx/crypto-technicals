import { tool } from 'ai';
import { z } from 'zod';
import { kv } from './kv';

// Define tools using strict, snake_case schemas for o3 compatibility
export const get_market_snapshot = tool({
  description: 'Fetches the high-level market overview data from the latest snapshot.',
  inputSchema: z.object({}).strict(),
  execute: async () => {
    const { json } = await kv.load();
    if (!json) return { error: 'snapshot unavailable' };
    const marketData: any = {};
    for (const horizon of json.meta.horizons_present || []) {
      if (json[horizon]?.market_overview) {
        marketData[horizon] = json[horizon].market_overview;
      }
    }
    return { meta: json.meta, market_data: marketData };
  }
});

export const get_coin_snapshot = tool({
  description: 'Fetches all available data for a single specified coin from the latest snapshot.',
  inputSchema: z.object({
    coin: z.string().describe("The coin's symbol, e.g., 'ethereum' or 'bitcoin'")
  }).strict(),
  execute: async ({ coin }) => {
    const { json } = await kv.load();
    if (!json) return { error: 'snapshot unavailable' };
    
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
    return { coin: coinLower, data: coinData };
  }
});

export const get_full_snapshot = tool({
  description: 'Fetches the entire, raw market snapshot. Warning: This is a large amount of data.',
  inputSchema: z.object({}).strict(),
  execute: async () => {
    const { json } = await kv.load();
    return json || { error: 'snapshot unavailable' };
  }
});

export const update_thesis = tool({
  description: 'Overwrites the current investment thesis markdown.',
  inputSchema: z.object({
    new_thesis: z.string().min(10).describe('The new thesis content in markdown format.')
  }).strict(),
  execute: async ({ new_thesis }) => {
    try {
      const fs = await import('fs/promises');
      const path = await import('path');
      const THESIS_FILE = path.join(process.cwd(), 'data', 'thesis.json');
      const thesisData = {
        thesis: new_thesis,
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
});

// Export tools for use with streamText
export const tools = {
  get_market_snapshot,
  get_coin_snapshot,
  get_full_snapshot,
  update_thesis,
};