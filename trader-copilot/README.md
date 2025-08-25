# CryptoCortex - AI-Powered Crypto Trading Assistant

**CryptoCortex** is a sophisticated dual-channel memory trading assistant that bridges the CryptoTechnicals data engine with an AI-powered chat interface. The system combines continuous market data generation with intelligent LLM analysis, creating a real-time trading intelligence platform.

## 🌟 Key Features

- **🧠 Dual-Channel Memory Architecture**: Lightweight chat history + heavy market data via tools
- **🤖 Direct OpenAI API Integration**: Native support for o3, gpt-5, and latest models
- **🔬 Deep Research Models**: o3-deep-research, o4-mini-deep-research with real-time progress streaming
- **💬 AI Trading Assistant**: Conversational market analysis with real-time tool calling
- **📊 Real-time Market Data**: Live snapshots with intelligent data sectioning
- **📝 Persistent Investment Thesis**: Strategy tracking across sessions
- **🔄 Auto/Manual Polling Control**: Configurable UI refresh modes
- **🎯 Intelligent Data Retrieval**: market/coin/full data access patterns
- **🔐 Basic Authentication**: Secure single-user operation
- **⚡ Streaming Responses**: Real-time AI responses with tool execution visibility
- **📖 Rich Content Formatting**: Markdown rendering with clickable links and proper spacing

## 🚀 Quick Start

### Prerequisites

1. **Python CLI Backend Setup**: Set up the CryptoTechnicals CLI backend:
   ```bash
   # Navigate to root directory
   cd ..
   
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Create .env file with API keys
   cp .env.example .env
   # Edit .env and add your COINGECKO_API_KEY
   ```

2. **Environment Variables**: Create `.env.local` file in trader-copilot directory:
   ```bash
   BASIC_AUTH_TOKEN=dev-secret
   PYTHON_CMD=python3
   OPENAI_API_KEY=your_openai_api_key_here
   COINGECKO_API_KEY=your_coingecko_api_key_here
   ```

### Installation & Setup

1. **Install Dependencies**:
   ```bash
   npm install
   ```

2. **Run Development Server**:
   ```bash
   npm run dev
   ```

3. **Open Browser**: Navigate to [http://localhost:3000](http://localhost:3000)

4. **Authentication**: The app uses basic auth with the `BASIC_AUTH_TOKEN` from `.env.local`

## 🏗️ Architecture Overview

### Dual-Channel Memory System

**Channel 1 (Chat)**: Conversation history stored in LLM prompts (lightweight)
**Channel 2 (Snapshots)**: Heavy market data accessed via tool calls (cost-optimized)

```
Manual Refresh → Python CLI → Snapshot Files → KV Cache → Next.js API → OpenAI
                     ↑                             ↑
                Data Generation            Tool Access via Chat
```

### Component Structure

- **Chat Interface**: Streaming AI conversations with tool calling
- **Thesis Panel**: Persistent investment strategy management  
- **Price Ticker**: Real-time market overview display
- **Model Picker**: OpenAI model selection (gpt-4o, gpt-4o-mini)
- **Snapshot Viewer**: Direct access to latest market intelligence

## 🛠️ API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/chat-direct` | POST | Direct OpenAI API streaming with tool calling |
| `/api/snapshot` | GET | Market data access (dual-channel) |
| `/api/thesis` | GET/POST | Investment strategy management |
| `/api/refresh` | POST | Manual market data refresh |
| `/api/control` | GET/POST | Auto-polling control |
| `/api/status` | GET | Data freshness detection |

## 🔧 Configuration

### Market Data Sections

- **`market`** (default): Market overview only - minimal tokens
- **`coin`**: Specific coin data - focused analysis  
- **`full`**: Complete snapshot - comprehensive analysis

### OpenAI Models

- **gpt-4o**: Maximum capability for complex analysis
- **gpt-4o-mini**: Cost-optimized for routine queries
- **o3**: Latest reasoning model for advanced analysis
- **gpt-5**: Next-generation model with enhanced capabilities
- **o3-deep-research**: Multi-step research with web search (3-5 min response time)
- **o4-mini-deep-research**: Cost-optimized deep research model

## 📊 Data Pipeline Integration

CryptoCortex integrates with the CryptoTechnicals engine:

1. **Manual Refresh** triggers Python CLI to generate fresh snapshots
2. **KV Store** caches data with hash-based change detection  
3. **API Layer** provides intelligent data sectioning
4. **AI Tools** access market data on-demand via chat tools
5. **UI Components** display market overview and enable refresh control

**Note**: The system uses on-demand data generation triggered by manual refresh button or chat queries, rather than continuous background polling.

## 💾 Persistent Chat History

CryptoCortex features a sophisticated **multi-month chat history system** that preserves conversation context across sessions:

### Dynamic Context Loading
- **Context Budget**: 200,000 tokens (configurable via `CONTEXT_BUDGET_TOKENS`)
- **System Reserve**: 4,000 tokens reserved for system prompts and tools
- **Multi-Month Spanning**: Automatically loads conversation history across multiple months
- **Smart Clipping**: Walks files from newest to oldest, loading messages until token budget is reached

### Storage Architecture
- **NDJSON Format**: One file per month (`chat-2025-08.jsonl`) for efficient append-only writes
- **Reverse Traversal**: Reads files bottom-to-top (newest messages first) for optimal performance
- **Automatic Rotation**: New month = new file, old conversations automatically archived
- **Human Readable**: Files can be opened and read with any text editor

### API Endpoints
- `GET /api/chat-history?mode=context` - Multi-month context-aware loading (default)
- `GET /api/chat-history?mode=recent&limitTokens=50000` - Legacy single-month loading
- `GET /api/chat-history?mode=stats` - Chat history statistics
- `POST /api/chat-history` - Append new message
- `DELETE /api/chat-history` - Clear current month (testing only)

### Configuration Constants
```typescript
// Configurable in src/lib/chat-store.ts
export const CONTEXT_BUDGET_TOKENS = 200_000;  // Total budget for context
export const SYSTEM_RESERVE_TOKENS = 4_000;    // Reserved for system prompts
```

### Benefits
- **Seamless Continuity**: Chat survives browser refreshes, server restarts, model switches
- **Context Preservation**: AI can reference conversations from weeks or months ago
- **Token Efficient**: Only loads what fits in the model's context window
- **Performance Optimized**: O(1) append operations, efficient tail reads
- **Future Proof**: Easily adjustable when model context windows increase

**Example**: If you have 90k tokens in August and 80k in September, refreshing the UI in October will show ~170k tokens of seamless conversation history.

## 🔐 Security Features

- **Basic Authentication**: Environment-based user credentials
- **API Protection**: All endpoints secured with auth middleware
- **Local Deployment**: Designed for secure single-user operation
- **No External Dependencies**: Self-contained authentication system

## 🧪 Development Status

### ✅ Completed Features
- Complete Next.js 14 frontend with TypeScript
- Dual-channel memory architecture with KV store
- **Direct OpenAI API integration** (bypassing AI SDK compatibility issues)
- Auto/manual polling control with UI toggle
- Basic authentication system
- File-based NextJS ↔ Python CLI coordination
- Streaming responses with real-time tool execution
- Thesis management system
- **v0.3.2**: Fixed timestamp display and chat functionality
- **v0.3.3**: Fixed AI SDK tools integration - partial function calling
- **v0.4.0**: Complete direct OpenAI API implementation - 100% functional tools
- **v0.4.1**: Deep research models with real-time progress streaming and rich content formatting

### ✅ Fully Functional (Validated)
- **AI Function Calling**: Native tool calling with o3, gpt-5, and latest models
- **Market Data Access**: Live crypto data via smart tool selection (market/coin/full)
- **Thesis Management**: AI can update investment strategy via `update_thesis` tool  
- **Real-time Analysis**: Complete dual-channel architecture with token efficiency
- **Deep Research Models**: o3-deep-research, o4-mini-deep-research with progress streaming
- **Rich Content Display**: Clickable links, markdown formatting, proper spacing
- **Progress Visibility**: Real-time workflow tracking for long-running tasks

### 🔮 Next Priorities
1. Advanced trading tools (position sizing, risk management)
2. Chart integration for visual analysis
3. Portfolio tracking and performance analytics
4. Multi-timeframe analysis tools

## 📁 Project Structure

```
src/
├── app/
│   ├── api/           # API endpoints
│   ├── globals.css    # Tailwind CSS styles
│   ├── layout.tsx     # App layout
│   └── page.tsx       # Main trading interface
├── components/
│   ├── ChatDirect.tsx  # Direct OpenAI API chat interface  
│   ├── Chat.tsx        # Legacy AI SDK interface (deprecated)
│   ├── ThesisPanel.tsx # Strategy management
│   ├── PriceTicker.tsx # Market overview with polling controls
│   └── ui/             # shadcn/ui components
└── lib/
    ├── kv.ts           # Dual-channel memory (KV store)
    ├── openai-direct.ts # Direct OpenAI API tool definitions
    ├── tools.ts        # Legacy AI SDK tools (deprecated)
    └── auth.ts         # Authentication
```

## 🎯 Usage Examples

### Market Analysis
```
"Analyze current ETH technicals and provide entry points"
"Compare BTC and SOL momentum indicators"
"What's the overall market sentiment based on dominance?"
```

### Strategy Management  
```
"Update my thesis: focusing on Layer 1 scaling solutions"
"Review my current thesis against market conditions"
"Adjust risk parameters for current volatility regime"
```

### Data Exploration
```
"Show me the latest snapshot for just Bitcoin"
"Get full market overview with all coins"  
"Refresh market data and analyze changes"
```

### Deep Research Queries
```
"Research the latest developments in Layer 2 scaling solutions"
"Analyze Peter Thiel's cryptocurrency investment strategy with sources"
"Deep dive into DeFi protocol revenue models with market data"
```

**Note**: Deep research models (o3-deep-research, o4-mini-deep-research) provide comprehensive analysis with web search and take 3-5 minutes. Progress is shown in real-time.

---

**Built with**: Next.js 14, TypeScript, Tailwind CSS, Direct OpenAI API, shadcn/ui  
**Integration**: CryptoTechnicals Python CLI backend  
**Version**: 0.4.1 - Deep Research Models with Progress Streaming  
**Last Updated**: August 25, 2025 11:54 AM CT

## 🔗 Related Documentation
- [Development Logs](./devlogs/) - Detailed development progress
- [Dual-Channel Memory Specs](../specs/UI-LLM-integration-specs.md) - Architecture documentation
- [CryptoTechnicals CLI](../CLAUDE.md) - Backend data engine documentation
