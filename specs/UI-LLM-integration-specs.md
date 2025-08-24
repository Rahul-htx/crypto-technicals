Trader Copilot
##############
Aug 23 2025

Executive Summary
-----------------
Trader‑Copilot is a lightweight, multi‑model trading copilot that combines a *living* investment thesis with live market snapshots in every LLM turn. By persisting the thesis in React state and keeping heavy snapshots outside the prompt—fetched only when an LLM calls the `getSnapshot` tool—the system slashes token costs, preserves latency, and maintains full data fidelity (dual‑channel memory).  

A Python CLI continuously produces `latest_snapshot.json`, while a Next.js 14 front‑end built with the Vercel AI SDK streams conversations, exposes tools (`getSnapshot`, `updateThesis`), and lets users switch between OpenAI models **o3**, **o3‑deep‑research**, and **o4‑mini‑deep‑research** via a radio selector. 
Users and (optionally) the LLM can edit the thesis, refresh snapshots, and generate trade ideas without ever leaving the chat interface.
Trader-Copilot ChatBot

⸻

0.  High-level objectives  (conviction 9/10)
	1.	Live thesis & snapshot as first-class objects (not static prompt text).
	2.	Dual-channel context:
	•	Conversation history goes into the prompt.
	•	Snapshot lives outside and is fetched on-demand via a tool call.
	3.	Multi-model routing via a radio selector (initial set: o3, o3-deep-research, o4-mini-deep-research).

⸻

1.  Tech stack

Layer	Choice	Rationale
Data engine	Existing crypto_technicals Python CLI	Already working; just add --serve (writes latest_snapshot.json to disk & emits a websocket “snapshot_updated”).
Backend API	Next.js 14 / App Router (Node 18)	Built-in API routes, Vercel AI SDK examples.
AI orchestration	@ai-sdk/core v5 & @ai-sdk/react	Native tool-calling & streaming  ￼ ￼
UI	React (shadcn/ui), Tailwind	Fast to scaffold.
Persistence	Tiny SQLite via Prisma (thesis versions, audit log).	
Real-time	ws (server) + React context for live updates.	
Deployment	Vercel (edge) or AWS Amplify; Python job on a scheduled container or GitHub Actions.	


⸻

2.  Model catalogue & limits

ID	Context window	Max output	Notes
o3	200 k tokens	100 k	Base reasoning model  ￼
o3-deep-research	200 k	100 k	Optimised for multi-source research  ￼
o4-mini-deep-research	200 k	100 k	Faster, cheaper “mini” flavour  ￼

(Future models just drop into the router config.)

⸻

3.  Data contracts

3.1  SystemContext

interface SystemContext {
  thesis: string;            // markdown
  snapshot: Snapshot;        // JSON from crypto_technicals
  updatedAt: string;         // ISO-8601
  updatedBy: string;         // user / model id
}

3.2  REST

Verb	Route	Payload	Returns
GET	/api/snapshot	—	Snapshot
GET	/api/thesis	—	{ thesis, updatedAt, updatedBy }
PATCH	/api/thesis	{ thesis }	200 OK
POST   /api/refresh     —                          202 Accepted (triggers immediate snapshot refresh)

3.3  WebSocket

wss://…/snapshot pushes { type:'snapshot_updated', hash:'abcd', at:Date }

⸻

4.  AI SDK integration

4.1  Tools

import { z } from 'zod';

export const tools = {
  getSnapshot: {
    parameters: z.object({
      section: z.enum(['full','market','coin']).default('full'),
      coin:    z.string().optional()
    }),
    description:
      'Fetches the latest market snapshot. Use section="coin" when you only need data for a single ticker.',
  },

  updateThesis: {
    parameters: z.object({
      newThesis: z.string()
    }),
    description: 'Overwrite the current investment thesis markdown.'
  }
};

4.2  API call template

import { streamText } from 'ai';
import { openai } from '@ai-sdk/openai';

const result = await streamText({
  model: openai(selectedModelId),
  messages,                 // chat history
  system: renderSystemMeta(), // DO *NOT* embed snapshot here
  tools,
  onToolCall: handleToolCall
});

	•	Multi-step tool resolution via stopWhen if the model chains calls  ￼.

⸻

5.  Front-end modules

/app
 ├─ api/
 │   ├─ snapshot/route.ts        # GET handler
 │   └─ thesis/route.ts          # GET / PATCH
 ├─ components/
 │   ├─ Chat.tsx                 # useChat hook
 │   ├─ ModelPicker.tsx
 │   ├─ ModelPicker.tsx          # default = 'o4-mini-deep-research'; persists selection in localStorage
 │   ├─ ThesisPanel.tsx          # live markdown editor
 │   └─ SnapshotBadge.tsx        # hash + “refresh” btn
 │   ├─ PriceTicker.tsx          # shows live coin prices + last‑updated timestamp
 │   ├─ SnapshotViewer.tsx      # collapsible panel to inspect raw snapshot JSON
 ├─ context/SystemCtx.tsx        # React context (Zustand)
 └─ pages/index.tsx              # layout

**UI layout (high‑level)**  
┌────────────┬──────────────────────┐  
│ ModelPicker│ Chat window (stream) │  
│ Thesis     │                      │  
│ Prices     │                      │  
└────────────┴──────────────────────┘  
*Left column* (narrow, scroll‑locked):  
  • ModelPicker (radio buttons)  
  • ThesisPanel (editable markdown)  
  • PriceTicker (latest prices & timestamp)  
*Right column* (flex‑1):  
  • Chat component streaming messages.  
SnapshotBadge appears beside the Thesis header to indicate freshness and manual “Refresh Now” control.  
A toggle button in the PriceTicker header opens a collapsible “Snapshot Viewer” so you can sanity‑check the raw JSON whenever needed.

⸻

6.  Backend workflow
	1.	Python job finishes → writes latest_snapshot.json.
	2.	Emits websocket snapshot_updated.
	3.	Next.js listener updates cached snapshot & broadcasts to clients.
	4.	React context receives, sets systemCtx.snapshot, UI shows “Snapshot refreshed 12 s ago”.
	5.  UI “Refresh Now” button → POST /api/refresh → watcher triggers `generate_snapshot()` immediately and broadcasts `snapshot_updated`.

⸻

7.  Cost / latency safeguard (MANDATORY)
	•	Default tool behaviour returns only market_overview unless section:'full' OR the call requests a coin.
	•	This caps average tool payload to <20 k tokens while still allowing full access when explicitly needed.

⸻

8.  Security & auth (bear-minimum)
	•	Simple Basic Auth header for REST & WS (JWT later).
	•	CLI writes snapshots to a directory outside web root.

⸻

9.  Testing

Layer	Tool	Aim
Python	pytest	Snapshot integrity, hash change detection
Node	vitest	Tool-call resolver, REST controllers
Front	Playwright	Model switch & thesis edit flows


⸻

10.  Milestones

#	Deliverable	Target
1	Snapshot API + manual upload	Week 1
2	Chat UI with model picker, getSnapshot tool	Week 2
3	Thesis editor + updateThesis tool	Week 3
4	Websocket live snapshot + cron run	Week 4
5	Persistence & basic auth	Week 5


⸻

11.  Future extensions
	•	Diff-only snapshot tool (getSnapshotDiff(sinceHash)), reducing tokens further.
	•	Vector search over historical snapshots for back-testing queries.
	•	Fine-grained roles: analyst vs. trader with different editing rights.
	•	Scheduled auto-thesis updates driven by LLM (tool call on cron).

⸻

Yes — the spec already adopts Option C (“dual-channel memory”) as the mandatory architecture.
Below is a deeper drill-down so your programmer can implement it without ambiguity.

⸻

Dual-Channel Memory – detailed design  (conviction 9 / 10)

Channel	Stored where	Lifetime	Access cost	Who controls it
Conversational context	Prompt tokens	One turn	$ per token, O(n²) attention	Chat orchestrator
Market snapshot (and any other heavy reference data)	External store (RAM + REST/WS endpoint)	Until next snapshot generated	0 $ per turn until tool-fetched	Tool resolver

Essential truth

Keep large, mostly-static blobs out of every prompt; instead expose them through cheap, on-demand calls.
This isolates rising chat history from static reference data and gives you linear cost growth rather than quadratic.

⸻

1.  Data stores

1.1  In-memory KV (Edge-runtime friendly)

// simple global cache in Next.js
const kv = {
  snapshot: {json: null as Snapshot|null, hash: '', loadedAt: 0},
  load: async () => {
    const file = await fs.readFile(SNAPSHOT_PATH,'utf-8');
    const hash = sha256(file);
    if (hash !== kv.snapshot.hash) kv.snapshot = { json: JSON.parse(file), hash, loadedAt: Date.now() };
    return kv.snapshot;
  }
};

Runs inside the Vercel Function or Node process; auto-reloads when the file changes.

1.2  WebSocket push
	•	Python job → on success: echo '{"type":"snapshot_updated","hash":"abcd"}' | websocat ws://localhost:8787/snapshot

React client subscribes:

ws.onmessage = (e) => {
  if (e.data.type === 'snapshot_updated') queryClient.invalidateQueries(['snapshot']);
};


⸻

2.  Tool interface (AI SDK)

/* tools/getSnapshot.ts */
import { z } from 'zod';
import { kv } from '@/lib/kv';

export const getSnapshotTool = {
  name: 'getSnapshot',
  description: 'Retrieves parts of the latest market snapshot',
  parameters: z.object({
    section: z.enum(['full','market','coin']).default('market'),
    coin: z.string().optional()
  }),
  execute: async ({section, coin}) => {
    const { json } = await kv.load();
    if (section === 'full')        return json;
    if (section === 'market')      return json.market_overview;
    if (section === 'coin') {
      if (!coin) throw new Error('coin required for section="coin"');
      return json.coins?.[coin.toLowerCase()] ?? { error:`coin ${coin} not found`};
    }
  }
};

Size guard:
	•	market_overview ~5 KB
	•	single coin ~3 KB
	•	full snapshot allowed but counts against 200 k context, so model should request it only when needed.

⸻

3.  Prompt construction

function buildPrompt(systemCtx: SystemContext, chat: ChatMessage[]) {
  const systemHeader = `
### Investment Thesis  
Last updated: ${systemCtx.updatedAt} by ${systemCtx.updatedBy}

${systemCtx.thesis}
  `.trim();

  return [
    { role:'system', content: systemHeader },
    ...chat           // no snapshot in here!
  ];
}


⸻

4.  End-to-end call sequence

sequenceDiagram
User->>ChatUI: ask "What trades today?"
ChatUI->>Backend: POST /chat (payload: user msg)
Backend->>LLM: streamText({model, messages, tools:[getSnapshot,updateThesis]})
LLM-->>Backend: toolCall getSnapshot(section:'market')
Backend->>getSnapshot: resolve
getSnapshot-->>Backend: { total_market_cap: … }
Backend-->>LLM: toolResult
LLM-->>Backend: assistant content (trade ideas)
Backend-->>ChatUI: stream
ChatUI-->>User: reply


⸻

5.  Error handling & edge cases

Case	Behaviour
Snapshot missing / corrupt	Tool returns { error:'snapshot unavailable' }; model must handle.
Model repeatedly requests full snapshot > 3× in same turn	Abort tool call with error to avoid runaway cost.
Coin not found	Return stub { error:'coin X not in snapshot' }.
Out-of-date thesis update collision	Compare updatedAt; if remote newer, return 409 to UI to prompt user.


⸻

6.  Client-side caching rules  (recommended)
	1.	react-query key ['snapshot', hash] – hash from WS prevents stale reads.
	2.	['thesis','latest'] – revalidate every 30 s or on successful PATCH.
	3.	Do not cache tool results; the LLM re-requests what it needs.

⸻