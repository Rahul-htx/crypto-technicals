# Market Intelligence Integration for Trader Copilot

## Project Context

Trader Copilot is a cryptocurrency trading assistant that combines an investment thesis, real-time market data, and AI analysis to provide trading insights. The system currently has:

1. **Investment Thesis** (`data/thesis.json`) - Static trading strategy loaded into every conversation
2. **Market Snapshots** - Real-time data fetched via tools when needed
3. **Chat History** - Conversation context maintained across sessions

## Problem Statement

The AI assistant's knowledge is limited by its training data cutoff date. Critical market events, regulatory changes, and evolving trading principles that occur after this cutoff are invisible to the model. This creates a dangerous blind spot where the AI might make recommendations based on outdated assumptions.

Examples of missing critical information:
- Recent regulatory changes (e.g., "Genius Act" or other crypto legislation)
- Major exchange incidents or bankruptcies
- New market dynamics or correlation patterns
- Evolved trading principles based on recent market behavior

## Proposed Solution: Market Intelligence Module

### Architecture Overview

Implement a hybrid "Market Intelligence" system that provides both always-available crucial **intel** and detailed on-demand context:

```
┌─────────────────────────────────────────────────────────┐
│                    System Prompt                         │
│  ┌─────────────────┐  ┌─────────────────────────────┐  │
│  │ Investment      │  │ Market Intel Summary        │  │
│  │ Thesis          │  │ (Pinned: 300-500 words)     │  │
│  │ (Full)          │  │ • Critical news bullets     │  │
│  └─────────────────┘  │ • Core trading principles   │  │
│                       └─────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│                    Tool Access                           │
│  ┌─────────────────┐  ┌─────────────────────────────┐  │
│  │ Market          │  │ Market Intel Detail         │  │
│  │ Snapshots       │  │ (Full content via tool)     │  │
│  │                 │  │ • Comprehensive news        │  │
│  └─────────────────┘  │ • All trading principles    │  │
│                       │ • Historical context         │  │
│                       └─────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Implementation Specifications

#### 1. File Structure

Create `trader-copilot/data/market_intel.json`:

```json
{
  "last_updated": "2025-08-29T10:00:00Z",
  "updated_by": "manual",
  "pinned_summary": {
    "critical_updates": [
      "• US 'Genius Act' (Aug 28): Clear crypto regulatory framework passed, bullish for institutional adoption",
      "• Fed maintains hawkish stance: Higher rates continue to pressure risk assets",
      "• BTC ETF flows turning positive after 3-week outflow period"
    ],
    "active_principles": [
      "• Risk-off mode: Only deploy capital on 8/10+ conviction trades",
      "• Alt exposure suspended until BTC.D < 56% and breadth improves",
      "• Preserve 50%+ cash until BTC flush-buy zone ($104-108k) or breakout >$120k"
    ]
  },
  "detail": {
    "recent_news": [
      {
        "date": "2025-08-28",
        "headline": "US Senate Passes 'Genius Act' Clarifying Digital Asset Regulations",
        "summary": "The act provides a clear legal framework for cryptocurrencies, distinguishing between securities and commodities. Expected to reduce regulatory uncertainty and encourage institutional adoption, particularly benefiting BTC and ETH.",
        "impact": "bullish",
        "confidence": "high",
        "source": "https://example.com/genius-act-details"
      },
      {
        "date": "2025-08-27",
        "headline": "Major DeFi Protocol Suffers $50M Exploit",
        "summary": "XYZ Protocol's lending pools were drained due to a reentrancy bug. While contained to one protocol, it reinforces concerns about DeFi security and may delay institutional DeFi adoption.",
        "impact": "bearish",
        "confidence": "medium",
        "source": "https://example.com/defi-exploit"
      }
    ],
    "trading_principles": {
      "risk_management": [
        "Never add to losing altcoin positions",
        "Stop losses are mandatory on all trades except BTC accumulation zones",
        "Position size inversely proportional to volatility (use ATR-based sizing)"
      ],
      "entry_criteria": [
        "Minimum 8/10 conviction score required (weighted: 40% macro, 30% technicals, 20% on-chain, 10% sentiment)",
        "Volume confirmation required: 1.5x 30-day average for breakouts",
        "Multiple timeframe alignment: Daily, Weekly, and Monthly trends must agree"
      ],
      "market_regime": [
        "Risk-off indicators: BTC.D > 56%, negative breadth, declining total market cap",
        "Risk-on requires: BTC+ETH reclaim daily 20 EMA, breadth improvement, BTC.D rollover"
      ]
    }
  }
}
```

#### 1A. JSON Schema (formal)

Define a JSON-Schema to validate `market_intel.json`. Save as `specs/market_intel.schema.json` and use it in CI or the update tool to ensure structural integrity.

```jsonc
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "MarketIntel",
  "type": "object",
  "required": ["last_updated", "pinned_summary", "detail"],
  "properties": {
    "last_updated":   { "type": "string", "format": "date-time" },
    "updated_by":     { "type": "string" },
    "pinned_summary": {
      "type": "object",
      "required": ["critical_updates", "active_principles"],
      "properties": {
        "critical_updates":  { "type": "array", "items": { "type": "string" } },
        "active_principles": { "type": "array", "items": { "type": "string" } }
      }
    },
    "detail": {
      "type": "object",
      "required": ["recent_news", "trading_principles"],
      "properties": {
        "recent_news": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["date", "headline", "summary"],
            "properties": {
              "date":       { "type": "string", "format": "date" },
              "headline":   { "type": "string" },
              "summary":    { "type": "string" },
              "impact":     { "type": "string", "enum": ["bullish", "bearish", "neutral"] },
              "confidence": { "type": "string", "enum": ["high", "medium", "low"] },
              "source":     { "type": "string", "format": "uri" }
            }
          }
        },
        "trading_principles": {
          "type": "object",
          "additionalProperties": {
            "type": "array",
            "items": { "type": "string" }
          }
        }
      }
    }
  }
}
```

#### 1B. Concurrency & Locking

Multiple agents (human or AI) **can** invoke `update_market_intel`.  The implementation **must** guard against race conditions:

* Use a file-level mutex / advisory lock when writing `market_intel.json` (e.g. `flock` on POSIX or a `lockfile` npm lib).
* If a write conflict occurs, the second writer reloads the latest file, reapplies its change, and retries.
* Each update should stamp a new ISO timestamp in `last_updated` and include `updated_by` (userId or `ai-agent`).

#### 1C. Versioning & Audit Trail

Maintain an append-only log under `trader-copilot/data/market_intel_history/` with filename `<ISO_TIMESTAMP>.json` containing the full pre-change document.  This allows rollback and forensic analysis.

#### 1D. Auth & Permissions

Both `get_market_intel` and `update_market_intel` routes are protected by the existing auth middleware.  Only authenticated users **or** the AI runtime (server token) may call them.

#### 2. System Prompt Modification

Modify `trader-copilot/src/lib/openai-direct.ts` and `trader-copilot/src/app/api/chat/route.ts`:

**In the `buildSystemPrompt()` function:**

```typescript
export async function buildSystemPrompt(): Promise<string> {
  try {
    const fs = await import('fs/promises');
    const path = await import('path');
    
    const THESIS_FILE = path.join(process.cwd(), 'data', 'thesis.json');
    const MARKET_INTEL_FILE = path.join(process.cwd(), 'data', 'market_intel.json');
    
    // Load thesis (existing code)
    let thesisSection = '# Investment Thesis\n*No thesis available*';
    try {
      const data = await fs.readFile(THESIS_FILE, 'utf-8');
      const thesisData = JSON.parse(data);
      thesisSection = `# Investment Thesis
Last updated: ${thesisData.updatedAt} by ${thesisData.updatedBy}

${thesisData.thesis}`;
    } catch {
      // Use default
    }
    
    // Load market intelligence summary (NEW)
    let marketIntelSection = '';
    try {
      const data = await fs.readFile(MARKET_INTEL_FILE, 'utf-8');
      const marketIntel = JSON.parse(data);
      
      marketIntelSection = `
# Market Intelligence Summary
Last updated: ${marketIntel.last_updated}

## Critical Updates
${marketIntel.pinned_summary.critical_updates.join('\n')}

## Active Trading Principles
${marketIntel.pinned_summary.active_principles.join('\n')}

For detailed news and comprehensive principles, use the `get_market_intel` tool.`;
    } catch {
      marketIntelSection = '\n# Market Intelligence\nNo market intelligence available. Use `update_market_intel` to add current events.';
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

## Available Tools
- get_market_snapshot: Access market overview data
- get_coin_snapshot: Get data for a specific coin
- get_full_snapshot: Get complete snapshot (use sparingly)
- get_market_intel: Access detailed news and trading principles
- update_thesis: Modify the investment thesis
- update_market_intel: Add or update market intelligence`;
  } catch (error) {
    console.error('Error building system prompt:', error);
    return 'You are Trader Copilot, a cryptocurrency trading assistant.';
  }
}
```

#### 3. New Tool Implementation

Add two new tools to the tools configuration:

**get_market_intel tool:**
```typescript
{
  name: 'get_market_intel',
  description: 'Get detailed market intelligence including recent news and trading principles',
  parameters: z.object({
    section: z.enum(['all', 'news', 'principles']).optional().default('all'),
    days_back: z.number().optional().default(7).describe('For news section, how many days back to retrieve')
  }),
  execute: async ({ section, days_back }) => {
    const fs = await import('fs/promises');
    const path = await import('path');
    const MARKET_INTEL_FILE = path.join(process.cwd(), 'data', 'market_intel.json');
    
    try {
      const data = await fs.readFile(MARKET_INTEL_FILE, 'utf-8');
      const marketIntel = JSON.parse(data);
      
      if (section === 'news') {
        const cutoffDate = new Date();
        cutoffDate.setDate(cutoffDate.getDate() - days_back);
        const recentNews = marketIntel.detail.recent_news.filter(
          item => new Date(item.date) >= cutoffDate
        );
        return { news: recentNews, last_updated: marketIntel.last_updated };
      } else if (section === 'principles') {
        return { principles: marketIntel.detail.trading_principles, last_updated: marketIntel.last_updated };
      }
      
      return marketIntel.detail;
    } catch (error) {
      return { error: 'Failed to load market intelligence' };
    }
  }
}
```

**update_market_intel tool:**
```typescript
{
  name: 'update_market_intel',
  description: 'Add or update market intelligence (news or principles)',
  parameters: z.object({
    update_type: z.enum(['add_news', 'update_summary', 'add_principle']),
    content: z.object({
      // For add_news
      headline: z.string().optional(),
      summary: z.string().optional(),
      impact: z.enum(['bullish', 'bearish', 'neutral']).optional(),
      confidence: z.enum(['high', 'medium', 'low']).optional(),
      source: z.string().optional(),
      
      // For update_summary
      critical_updates: z.array(z.string()).optional(),
      active_principles: z.array(z.string()).optional(),
      
      // For add_principle
      category: z.enum(['risk_management', 'entry_criteria', 'market_regime']).optional(),
      principle: z.string().optional()
    })
  }),
  execute: async ({ update_type, content }) => {
    // TODO: implement concurrency-safe update with schema validation and history snapshot
  }
}
```

#### 4. Curation Workflow

The market intelligence should be updated through:

1. **Manual updates**: Edit `market_intel.json` directly for major events
2. **AI-assisted updates**: The chatbot can use `update_market_intel` when it encounters significant information
3. **Future automation**: Build a news aggregator that populates the detail section, with AI summarizing into pinned_summary

#### 5. Token Budget Management (approximate)

With this hybrid approach:
- **Pinned summary**: ~300-500 words ≈ 400-600 tokens (minimal overhead)
- **Full detail**: Unlimited size, only loaded when requested via tool
- **Total system prompt**: Thesis (~1000 tokens) + Market Intel Summary (~600 tokens) + Base prompt (~500 tokens) ≈ 2100 tokens total

This leaves ~197,900 tokens for conversation history and tool responses.

## Implementation Order

1. Create the `market_intel.json` file with initial content
2. Modify `buildSystemPrompt()` in both route files to include the pinned summary
3. Add the two new tools (`get_market_intel` and `update_market_intel`) to the tools configuration
4. Test the system with various scenarios:
   - Asking about recent news (should trigger tool use)
   - Making trading decisions (should consider pinned summary)
   - Adding new market intelligence via the update tool

## Success Criteria

- The AI always has access to critical recent developments via the pinned summary
- Detailed context is available on-demand without bloating the prompt
- The system can explain its recommendations in light of recent news/events
- Market intelligence can be updated without code changes
- Token usage remains efficient and predictable

This design ensures the Trader Copilot remains informed about post-training events while maintaining efficient token usage and system performance.