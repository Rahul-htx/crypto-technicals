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

## Proposed Solution: Hierarchical Memory System

### Architecture Overview

Implement a hierarchical memory system with "core" stable facts and "diff" recent changes, both pinned to every conversation turn, plus on-demand retrieval for detailed context:

```
┌──────────────────────────────────────────────────────────────┐
│                    System Prompt (Every Turn)                 │
│  ┌─────────────────┐  ┌────────────────────────────────────┐│
│  │ Investment      │  │ Hierarchical Memory                │ │
│  │ Thesis          │  │                                    │ │
│  │ (Full)          │  │ ┌─────────────────────────────┐   │ │
│  └─────────────────┘  │ │ Core Summary (1-2k words)    │   │ │
│                       │ │ • Stable market truths       │   │ │
│                       │ │ • Enduring principles        │   │ │
│                       │ │ • Regulatory framework       │   │ │
│                       │ └─────────────────────────────┘   │ │
│                       │                                    │ │
│                       │ ┌─────────────────────────────┐   │ │
│                       │ │ Diff Summary (1-3k words)    │   │ │
│                       │ │ • Recent breaking news       │   │ │
│                       │ │ • Temporary market events    │   │ │
│                       │ │ • Pending promotions         │   │ │
│                       │ └─────────────────────────────┘   │ │
│                       └────────────────────────────────────┘│
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    Tool Access (On-Demand)                    │
│  ┌─────────────────┐  ┌────────────────────────────────────┐│
│  │ Market          │  │ Retrievable Memory                 │ │
│  │ Snapshots       │  │ • Full historical archive          │ │
│  │                 │  │ • Detailed news with sources       │ │
│  └─────────────────┘  │ • One-off events & edge cases     │ │
│                       │ • Vector DB for semantic search    │ │
│                       └────────────────────────────────────┘│
└──────────────────────────────────────────────────────────────┘
```

### Core/Diff Memory Management

#### Hierarchical Structure
1. **Core Summary (1-2k words)**
   - Stable, enduring market facts and principles
   - Regulatory frameworks that persist across sessions
   - Fundamental trading rules that rarely change
   - Updated only when facts become permanently established

2. **Diff Summary (1-3k words)**
   - Breaking news and recent developments
   - Temporary market conditions and events
   - Items pending promotion to core
   - Automatically timestamped for age tracking

3. **Promotion Logic**
   - Diff items promoted to core after:
     - Configurable time threshold (e.g., 48 hours or 5 conversation turns)
     - LLM-based curation confirming stability
     - Human approval for high-impact changes
   - Each diff item includes metadata:
     ```json
     {
       "id": "unique-id",
       "content": "text",
       "created_at": "2025-08-29T10:00:00Z",
       "hit_count": 5,
       "confidence": 0.85,
       "promotion_eligible": true
     }
     ```

4. **Token Budget Management**
   - Fixed allocation: 10k tokens max for core + diff combined
   - Prioritization: core takes precedence, diff truncated if needed
   - Token counting using tiktoken at build time, not request time
   - Auto-compression when approaching limits

### Implementation Safeguards

#### 1. Promotion/Pruning Guards
- **Core-bloat prevention**: 
  - Hard ceiling of 12k tokens for core
  - "last-verified" timestamp on every core item
  - Stale item detection: unreferenced for 30+ days triggers review
  - Forced compression or demotion when ceiling approached

- **Noisy period handling**:
  - Mini-topic summarization during high-volume events
  - Raw entries preserved in retrievable memory
  - Batch similar diff items into single summary chunks

#### 2. LLM Curation Reliability
- **Hallucination prevention**:
  - Confidence scores (0-1) required for all promotions
  - Citation requirement (URL, source ID, or "human-provided")
  - Promotions < 0.8 confidence auto-rejected to human review
  
- **Health monitoring**:
  - Last successful curation timestamp tracked
  - Alert if >6 hours without successful run
  - Fallback to manual mode on repeated failures

#### 3. Concurrency & Data Integrity
- **Race condition prevention**:
  - Optimistic locking with version numbers
  - Transactional updates using SQLite/Postgres
  - Schema versioning for backward compatibility

- **Audit trail**:
  - Append-only promotion log with full diffs
  - Weekly snapshots stored in version control
  - Emergency rollback capability with regex purging

#### 4. Cost Optimization
- **Efficient curation**:
  - First pass with gpt-5-mini for proposal generation
  - Only use premium models for verification
  - Run curation only when diff_size > threshold OR time > 4h
  - Low priority queue for non-urgent updates

#### 5. Retrieval Integration
- **Deduplication**:
  - Mark vector DB entries as "archived" when promoted to core
  - Re-embed promoted text to maintain searchability
  - Track embedding hashes to skip redundant operations

### Implementation Specifications

#### 1. File Structure

Create `trader-copilot/data/market_intel.json`:

```json
{
  "version": 2,
  "last_updated": "2025-08-29T10:00:00Z",
  "updated_by": "manual",
  "core": {
    "last_verified": "2025-08-29T10:00:00Z",
    "items": [
      {
        "id": "core-001",
        "content": "US 'Genius Act' (Aug 28): Establishes clear crypto regulatory framework distinguishing securities from commodities",
        "category": "regulatory",
        "last_verified": "2025-08-29T10:00:00Z",
        "reference_count": 15
      },
      {
        "id": "core-002", 
        "content": "Risk management: Never add to losing altcoin positions; mandatory stops except BTC accumulation zones",
        "category": "principle",
        "last_verified": "2025-08-29T10:00:00Z",
        "reference_count": 23
      },
      {
        "id": "core-003",
        "content": "Entry criteria: Minimum 8/10 conviction (40% macro, 30% technicals, 20% on-chain, 10% sentiment)",
        "category": "principle",
        "last_verified": "2025-08-29T10:00:00Z",
        "reference_count": 31
      }
    ]
  },
  "diff": {
    "items": [
      {
        "id": "diff-001",
        "content": "Fed maintains hawkish stance: Higher rates continue pressuring risk assets",
        "created_at": "2025-08-29T08:00:00Z",
        "hit_count": 3,
        "confidence": 0.9,
        "promotion_eligible": false,
        "source": "https://example.com/fed-minutes"
      },
      {
        "id": "diff-002",
        "content": "BTC ETF flows turning positive after 3-week outflow period",
        "created_at": "2025-08-28T16:00:00Z",
        "hit_count": 7,
        "confidence": 0.85,
        "promotion_eligible": true,
        "source": "https://example.com/etf-flows"
      },
      {
        "id": "diff-003",
        "content": "Major DeFi protocol exploit ($50M) reinforces security concerns",
        "created_at": "2025-08-27T14:00:00Z",
        "hit_count": 2,
        "confidence": 0.7,
        "promotion_eligible": false,
        "source": "https://example.com/defi-exploit"
      }
    ]
  },
  "metadata": {
    "core_token_count": 487,
    "diff_token_count": 392,
    "total_token_count": 879,
    "last_curation_run": "2025-08-29T06:00:00Z",
    "next_curation_due": "2025-08-29T10:00:00Z"
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
  "required": ["version", "last_updated", "core", "diff", "metadata"],
  "properties": {
    "version":        { "type": "number", "const": 2 },
    "last_updated":   { "type": "string", "format": "date-time" },
    "updated_by":     { "type": "string" },
    "core": {
      "type": "object",
      "required": ["last_verified", "items"],
      "properties": {
        "last_verified": { "type": "string", "format": "date-time" },
        "items": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["id", "content", "category", "last_verified", "reference_count"],
            "properties": {
              "id":               { "type": "string", "pattern": "^core-\\d+$" },
              "content":          { "type": "string", "minLength": 10, "maxLength": 500 },
              "category":         { "type": "string", "enum": ["regulatory", "principle", "market_structure", "macro"] },
              "last_verified":    { "type": "string", "format": "date-time" },
              "reference_count":  { "type": "integer", "minimum": 0 }
            }
          }
        }
      }
    },
    "diff": {
      "type": "object",
      "required": ["items"],
      "properties": {
        "items": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["id", "content", "created_at", "hit_count", "confidence", "promotion_eligible"],
            "properties": {
              "id":                  { "type": "string", "pattern": "^diff-\\d+$" },
              "content":             { "type": "string", "minLength": 10, "maxLength": 500 },
              "created_at":          { "type": "string", "format": "date-time" },
              "hit_count":           { "type": "integer", "minimum": 0 },
              "confidence":          { "type": "number", "minimum": 0, "maximum": 1 },
              "promotion_eligible":  { "type": "boolean" },
              "source":              { "type": "string", "format": "uri" }
            }
          }
        }
      }
    },
    "metadata": {
      "type": "object",
      "required": ["core_token_count", "diff_token_count", "total_token_count"],
      "properties": {
        "core_token_count":    { "type": "integer", "minimum": 0 },
        "diff_token_count":    { "type": "integer", "minimum": 0 },
        "total_token_count":   { "type": "integer", "minimum": 0 },
        "last_curation_run":   { "type": "string", "format": "date-time" },
        "next_curation_due":   { "type": "string", "format": "date-time" }
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
  description: 'Get full market intelligence including all core facts, diff items, and metadata',
  parameters: z.object({
    include_archived: z.boolean().optional().default(false).describe('Include archived/historical entries from vector DB')
  }),
  execute: async ({ include_archived }) => {
    const fs = await import('fs/promises');
    const path = await import('path');
    const MARKET_INTEL_FILE = path.join(process.cwd(), 'data', 'market_intel.json');
    
    try {
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
      if (include_archived) {
        // TODO: Query vector DB for historical items
        response.archived = [];
      }
      
      return response;
    } catch (error) {
      return { error: 'Failed to load market intelligence', details: error.message };
    }
  }
}
```

**update_market_intel tool:**
```typescript
{
  name: 'update_market_intel',
  description: 'Add to diff, promote to core, or perform maintenance on market intelligence',
  parameters: z.object({
    action: z.enum(['add_diff', 'promote_to_core', 'prune_stale', 'run_curation']),
    payload: z.object({
      // For add_diff
      content: z.string().optional().describe('New market event or update'),
      confidence: z.number().min(0).max(1).optional().default(0.8),
      source: z.string().optional(),
      
      // For promote_to_core
      diff_id: z.string().optional().describe('ID of diff item to promote'),
      category: z.enum(['regulatory', 'principle', 'market_structure', 'macro']).optional(),
      
      // For prune_stale
      days_threshold: z.number().optional().default(30),
      
      // For run_curation (no params needed)
    })
  }),
  execute: async ({ action, payload }) => {
    const fs = await import('fs/promises');
    const path = await import('path');
    const crypto = await import('crypto');
    const MARKET_INTEL_FILE = path.join(process.cwd(), 'data', 'market_intel.json');
    const HISTORY_DIR = path.join(process.cwd(), 'data', 'market_intel_history');
    
    // Implement file locking
    const lockfile = require('proper-lockfile');
    const release = await lockfile.lock(MARKET_INTEL_FILE);
    
    try {
      // Load current state
      const data = await fs.readFile(MARKET_INTEL_FILE, 'utf-8');
      const marketIntel = JSON.parse(data);
      
      // Save history snapshot
      const timestamp = new Date().toISOString();
      await fs.mkdir(HISTORY_DIR, { recursive: true });
      await fs.writeFile(
        path.join(HISTORY_DIR, `${timestamp}.json`),
        JSON.stringify(marketIntel, null, 2)
      );
      
      // Perform the requested action
      switch (action) {
        case 'add_diff':
          const newDiffId = `diff-${Date.now()}`;
          marketIntel.diff.items.push({
            id: newDiffId,
            content: payload.content,
            created_at: timestamp,
            hit_count: 0,
            confidence: payload.confidence,
            promotion_eligible: false,
            source: payload.source
          });
          break;
          
        case 'promote_to_core':
          const diffItem = marketIntel.diff.items.find(i => i.id === payload.diff_id);
          if (diffItem) {
            const newCoreId = `core-${Date.now()}`;
            marketIntel.core.items.push({
              id: newCoreId,
              content: diffItem.content,
              category: payload.category,
              last_verified: timestamp,
              reference_count: 0
            });
            // Remove from diff
            marketIntel.diff.items = marketIntel.diff.items.filter(i => i.id !== payload.diff_id);
          }
          break;
          
        case 'prune_stale':
          const threshold = new Date();
          threshold.setDate(threshold.getDate() - payload.days_threshold);
          marketIntel.core.items = marketIntel.core.items.filter(
            item => new Date(item.last_verified) > threshold || item.reference_count > 5
          );
          break;
          
        case 'run_curation':
          // This would call gpt-5-mini to analyze and suggest promotions
          // Implementation deferred to actual curation service
          return { message: 'Curation service not yet implemented' };
      }
      
      // Update metadata
      marketIntel.last_updated = timestamp;
      marketIntel.updated_by = 'ai-agent';
      
      // Recalculate token counts
      const tiktoken = require('tiktoken');
      const enc = tiktoken.encoding_for_model('gpt-4o');
      
      const coreText = marketIntel.core.items.map(i => i.content).join(' ');
      const diffText = marketIntel.diff.items.map(i => i.content).join(' ');
      
      marketIntel.metadata.core_token_count = enc.encode(coreText).length;
      marketIntel.metadata.diff_token_count = enc.encode(diffText).length;
      marketIntel.metadata.total_token_count = 
        marketIntel.metadata.core_token_count + marketIntel.metadata.diff_token_count;
      
      // Validate against schema
      const ajv = require('ajv');
      const schema = require('./specs/market_intel.schema.json');
      const validate = ajv.compile(schema);
      
      if (!validate(marketIntel)) {
        throw new Error(`Schema validation failed: ${JSON.stringify(validate.errors)}`);
      }
      
      // Write updated file
      await fs.writeFile(MARKET_INTEL_FILE, JSON.stringify(marketIntel, null, 2));
      
      return {
        success: true,
        action,
        token_usage: marketIntel.metadata.total_token_count,
        timestamp
      };
      
    } finally {
      // Always release the lock
      await release();
    }
  }
}
```

#### 4. Curation Workflow

The market intelligence should be updated through:

1. **Manual updates**: Edit `market_intel.json` directly for major events
2. **AI-assisted updates**: The chatbot can use `update_market_intel` when it encounters significant information
3. **Future automation**: Build a news aggregator that populates the detail section, with AI summarizing into pinned_summary

4. **Automated curation model**: All background promotion/pruning jobs should run on **`gpt-5-mini`** for cost-efficient first-pass summarisation before any higher-tier verification.

#### 5. Token Budget Management

With the hierarchical memory approach:
- **Core summary**: 1-2k words ≈ 1,300-2,600 tokens
- **Diff summary**: 1-3k words ≈ 1,300-3,900 tokens  
- **Combined ceiling**: 10,000 tokens max (enforced)
- **Total system prompt**: Thesis (~1,000 tokens) + Core+Diff (~5,000 tokens typical) + Base prompt (~500 tokens) ≈ 6,500 tokens

This leaves ~193,500 tokens for conversation history and tool responses, while providing much richer always-available context.

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

## Implementation Checklist

### Storage Layer
- [ ] Create tables/collections: 
  - `core_summary` (id PK, text, last_verified, version)
  - `diff_items` (id PK, text, created_at, hits, confidence, promotion_eligible)
  - `promotion_log` (id PK, timestamp, action, before, after, reason)
- [ ] Set up market_intel_history directory for audit trail
- [ ] Implement optimistic locking mechanism

### API Services  
- [ ] `/api/memory/core` GET/PUT endpoints
- [ ] `/api/memory/diff` GET/POST/DELETE endpoints  
- [ ] `/api/memory/promote` POST endpoint (LLM or human triggered)
- [ ] `/api/memory/health` GET endpoint for monitoring

### Background Jobs
- [ ] `diff-to-core-promotion` cron job (every 4 hours)
  - Uses gpt-5-mini for initial analysis
  - Filters by confidence > 0.8 and age > 48h
  - Batches promotions to minimize writes
- [ ] `core-staleness-audit` cron job (daily)
  - Marks items unreferenced for 30+ days
  - Compresses or archives stale content
- [ ] `token-budget-enforcer` (on every write)
  - Ensures core + diff < 10k tokens
  - Auto-compresses when approaching limit

### Utilities
- [ ] `truncateToTokens(text, maxTokens)` helper using tiktoken
- [ ] Schema validation middleware using AJV
- [ ] Vector DB integration for archived item retrieval
- [ ] Emergency rollback tool with regex pattern matching

### Monitoring & Alerts
- [ ] Dashboard showing:
  - Current token usage (core/diff/total)
  - Promotion queue length
  - Last successful curation timestamp
  - Core items by age and reference count
- [ ] Alerts for:
  - Curation failures (>6h without success)
  - Token budget exceeded
  - Schema validation errors
  - Lock contention issues

### Testing Requirements
- [ ] Unit tests for all promotion logic
- [ ] Integration tests with mock gpt-5-mini responses
- [ ] Load tests for concurrent updates
- [ ] Rollback/recovery scenario tests
- [ ] Token counting accuracy tests