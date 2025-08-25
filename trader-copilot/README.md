# Trader Copilot - AI-Powered Crypto Trading Assistant

**Trader Copilot** is a sophisticated dual-channel memory trading assistant that bridges the CryptoTechnicals data engine with an AI-powered chat interface. The system combines continuous market data generation with intelligent LLM analysis, creating a real-time trading intelligence platform.

## 🌟 Key Features

- **🧠 Dual-Channel Memory Architecture**: Lightweight chat history + heavy market data via tools
- **🤖 Direct OpenAI API Integration**: Native support for o3, gpt-5, and latest models
- **💬 AI Trading Assistant**: Conversational market analysis with real-time tool calling
- **📊 Real-time Market Data**: Live snapshots with intelligent data sectioning
- **📝 Persistent Investment Thesis**: Strategy tracking across sessions
- **🔄 Auto/Manual Polling Control**: Configurable UI refresh modes
- **🎯 Intelligent Data Retrieval**: market/coin/full data access patterns
- **🔐 Basic Authentication**: Secure single-user operation
- **⚡ Streaming Responses**: Real-time AI responses with tool execution visibility

## 🚀 Quick Start

### Prerequisites

1. **Python CLI Backend Running**: Ensure the CryptoTechnicals CLI is running in serve mode:
   ```bash
   cd ..
   python -m src.cli --serve --interval 60 --verbose
   ```

2. **Environment Variables**: Create `.env.local` file:
   ```bash
   OPENAI_API_KEY=your_openai_api_key
   COPILOT_USERNAME=your_username
   COPILOT_PASSWORD=your_password
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

4. **Login**: Use credentials from your `.env.local` file

## 🏗️ Architecture Overview

### Dual-Channel Memory System

**Channel 1 (Chat)**: Conversation history stored in LLM prompts (lightweight)
**Channel 2 (Snapshots)**: Heavy market data accessed via tool calls (cost-optimized)

```
Python CLI (60s) → Snapshot Files → KV Cache → Next.js API → OpenAI
                                     ↑
Manual Refresh ───────────────────────┘
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
| `/api/chat` | POST | Streaming AI chat with tool calling |
| `/api/snapshot` | GET | Market data access (dual-channel) |
| `/api/thesis` | GET/POST | Investment strategy management |
| `/api/refresh` | POST | Manual market data refresh |

## 🔧 Configuration

### Market Data Sections

- **`market`** (default): Market overview only - minimal tokens
- **`coin`**: Specific coin data - focused analysis  
- **`full`**: Complete snapshot - comprehensive analysis

### OpenAI Models

- **gpt-4o**: Maximum capability for complex analysis
- **gpt-4o-mini**: Cost-optimized for routine queries

## 📊 Data Pipeline Integration

Trader Copilot seamlessly integrates with the CryptoTechnicals engine:

1. **Python CLI** generates snapshots every 60 seconds
2. **KV Store** caches data with hash-based change detection  
3. **API Layer** provides intelligent data sectioning
4. **AI Tools** access fresh market data on-demand
5. **UI Components** display real-time market intelligence

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

### ✅ Fully Functional (Validated)
- **AI Function Calling**: Native tool calling with o3, gpt-5, and latest models
- **Market Data Access**: Live crypto data via smart tool selection (market/coin/full)
- **Thesis Management**: AI can update investment strategy via `update_thesis` tool  
- **Real-time Analysis**: Complete dual-channel architecture with token efficiency
- **Model Support**: o3, gpt-5 confirmed working; o3-deep-research, o4-mini-deep-research (API limitations)

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

---

**Built with**: Next.js 14, TypeScript, Tailwind CSS, Direct OpenAI API, shadcn/ui  
**Integration**: CryptoTechnicals Python CLI backend  
**Version**: 0.4.0 - Production-Ready AI Trading Assistant

## 🔗 Related Documentation
- [Development Logs](./devlogs/) - Detailed development progress
- [Dual-Channel Memory Specs](../specs/UI-LLM-integration-specs.md) - Architecture documentation
- [CryptoTechnicals CLI](../CLAUDE.md) - Backend data engine documentation
