# Trader Copilot - AI-Powered Crypto Trading Assistant

**Trader Copilot** is a sophisticated dual-channel memory trading assistant that bridges the CryptoTechnicals data engine with an AI-powered chat interface. The system combines continuous market data generation with intelligent LLM analysis, creating a real-time trading intelligence platform.

## 🌟 Key Features

- **🧠 Dual-Channel Memory Architecture**: Lightweight chat history + heavy market data via tools
- **💬 AI Trading Assistant**: Conversational market analysis with OpenAI integration
- **📊 Real-time Market Data**: Continuous snapshots from Python CLI backend
- **📝 Persistent Investment Thesis**: Strategy tracking across sessions
- **🔄 Manual Refresh**: On-demand market data updates
- **🎯 Intelligent Data Sectioning**: market/coin/full data retrieval options
- **🔐 Basic Authentication**: Secure single-user operation

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
- OpenAI integration with streaming responses
- Python CLI serve mode integration
- Basic authentication system
- File-based NextJS ↔ Python CLI coordination
- Manual refresh capability
- Thesis management system
- **v0.3.2**: Fixed timestamp display and chat functionality

### ⚠️ Known Issues
- **Tool Schema Format**: OpenAI function calling currently disabled due to schema validation errors
- **Workaround**: Chat works without tools, market data accessible via API endpoints

### 🔮 Next Priorities
1. Resolve OpenAI tool schema formatting issues
2. Enable complete AI tool integration
3. Advanced trading tools (position sizing, risk management)
4. Chart integration for visual analysis

## 📁 Project Structure

```
src/
├── app/
│   ├── api/           # API endpoints
│   ├── globals.css    # Tailwind CSS styles
│   ├── layout.tsx     # App layout
│   └── page.tsx       # Main trading interface
├── components/
│   ├── Chat.tsx       # AI conversation interface
│   ├── ThesisPanel.tsx # Strategy management
│   ├── PriceTicker.tsx # Market overview
│   └── ui/            # shadcn/ui components
└── lib/
    ├── kv.ts          # Dual-channel memory
    ├── tools.ts       # AI SDK tool definitions
    └── auth.ts        # Authentication
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

**Built with**: Next.js 14, TypeScript, Tailwind CSS, OpenAI API, shadcn/ui  
**Integration**: CryptoTechnicals Python CLI backend  
**Version**: 0.3.2 - Dual-Channel Memory Trading Assistant
