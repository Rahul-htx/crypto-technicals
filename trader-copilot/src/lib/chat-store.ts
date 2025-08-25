// NDJSON-based chat history storage
// One file per month, append-only for speed

import fs from 'fs/promises';
import path from 'path';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string; // ISO 8601
  model?: string; // for assistant messages
  toolCalls?: any[]; // for tool usage
  metadata?: {
    tokens?: number;
    duration?: number;
  };
}

const CHAT_DIR = path.join(process.cwd(), 'data', 'chat');

// Context budget constants
export const CONTEXT_BUDGET_TOKENS = 200_000;
export const SYSTEM_RESERVE_TOKENS = 4_000;

// Get the filename for a specific month
function getMonthlyFilename(date?: Date): string {
  const targetDate = date || new Date();
  const year = targetDate.getFullYear();
  const month = String(targetDate.getMonth() + 1).padStart(2, '0');
  return `chat-${year}-${month}.jsonl`;
}

// Get all existing chat log files, sorted newest to oldest
async function getChatLogFiles(): Promise<string[]> {
  await ensureChatDir();
  
  try {
    const files = await fs.readdir(CHAT_DIR);
    const chatFiles = files
      .filter(f => f.startsWith('chat-') && f.endsWith('.jsonl'))
      .sort()
      .reverse(); // Newest first
    
    return chatFiles.map(f => path.join(CHAT_DIR, f));
  } catch (error) {
    console.warn('Failed to read chat directory:', error);
    return [];
  }
}

// Generate unique message ID
function generateMessageId(): string {
  return `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

// Ensure chat directory exists
async function ensureChatDir(): Promise<void> {
  try {
    await fs.mkdir(CHAT_DIR, { recursive: true });
  } catch (error) {
    console.error('Failed to create chat directory:', error);
  }
}

// Append a message to the current month's log
export async function appendMessage(message: Omit<ChatMessage, 'id' | 'timestamp'>): Promise<ChatMessage> {
  await ensureChatDir();
  
  const fullMessage: ChatMessage = {
    ...message,
    id: generateMessageId(),
    timestamp: new Date().toISOString()
  };
  
  const filepath = path.join(CHAT_DIR, getMonthlyFilename());
  const line = JSON.stringify(fullMessage) + '\n';
  
  try {
    await fs.appendFile(filepath, line, 'utf-8');
    console.log(`💾 Saved message to chat history: ${fullMessage.id}`);
  } catch (error) {
    console.error('Failed to append message:', error);
  }
  
  return fullMessage;
}

/**
 * Load context-aware chat history across multiple months
 * 
 * Walks month files from newest to oldest, reading each file bottom-to-top,
 * collecting messages until we reach the token budget minus system reserve.
 * Returns messages in chronological order.
 * 
 * @param budgetOverride Optional override for CONTEXT_BUDGET_TOKENS
 * @returns Array of ChatMessage objects in chronological order
 */
export async function loadContext(budgetOverride?: number): Promise<ChatMessage[]> {
  const budget = budgetOverride || CONTEXT_BUDGET_TOKENS;
  const availableTokens = budget - SYSTEM_RESERVE_TOKENS;
  
  const chatFiles = await getChatLogFiles();
  const messages: ChatMessage[] = [];
  let totalTokens = 0;
  
  console.log(`🔍 Loading chat context with ${availableTokens} token budget from ${chatFiles.length} files`);
  
  // Walk files from newest to oldest
  for (const filepath of chatFiles) {
    try {
      const content = await fs.readFile(filepath, 'utf-8');
      const lines = content.trim().split('\n').filter(line => line.length > 0);
      
      // Read file bottom-to-top (newest messages first)
      for (let i = lines.length - 1; i >= 0; i--) {
        try {
          const message = JSON.parse(lines[i]) as ChatMessage;
          const messageTokens = message.metadata?.tokens || estimateTokens(message.content);
          
          // Check if adding this message would exceed our budget
          if (totalTokens + messageTokens > availableTokens && messages.length > 0) {
            console.log(`⚡ Context budget reached at ${totalTokens} tokens with ${messages.length} messages`);
            // Return messages in chronological order
            return messages.reverse();
          }
          
          messages.push(message); // Will be reversed at the end
          totalTokens += messageTokens;
        } catch (parseError) {
          console.warn('Skipping malformed message in', path.basename(filepath), ':', parseError);
        }
      }
    } catch (error: any) {
      if (error.code !== 'ENOENT') {
        console.warn('Failed to read chat file', path.basename(filepath), ':', error);
      }
    }
  }
  
  console.log(`📖 Loaded full context: ${messages.length} messages (≈${totalTokens} tokens) from ${chatFiles.length} files`);
  
  // Return messages in chronological order (oldest first)
  return messages.reverse();
}

// Legacy function - kept for backward compatibility
export async function loadRecent(limitTokens: number = 200000): Promise<ChatMessage[]> {
  await ensureChatDir();
  
  const filepath = path.join(CHAT_DIR, getMonthlyFilename());
  
  try {
    const content = await fs.readFile(filepath, 'utf-8');
    const lines = content.trim().split('\n').filter(line => line.length > 0);
    
    const messages: ChatMessage[] = [];
    let totalTokens = 0;
    
    // Process from most recent backwards
    for (let i = lines.length - 1; i >= 0; i--) {
      try {
        const message = JSON.parse(lines[i]) as ChatMessage;
        const messageTokens = message.metadata?.tokens || estimateTokens(message.content);
        
        if (totalTokens + messageTokens > limitTokens && messages.length > 0) {
          break; // Stop if we'd exceed token limit (but always include at least one message)
        }
        
        messages.unshift(message); // Add to beginning to maintain chronological order
        totalTokens += messageTokens;
      } catch (parseError) {
        console.warn('Skipping malformed message:', parseError);
      }
    }
    
    console.log(`📖 Loaded ${messages.length} messages (≈${totalTokens} tokens) from chat history`);
    return messages;
  } catch (error: any) {
    if (error.code === 'ENOENT') {
      console.log('No chat history found for current month');
      return [];
    }
    console.error('Failed to load chat history:', error);
    return [];
  }
}

// Load all messages from current month (no token limit)
export async function loadAll(): Promise<ChatMessage[]> {
  await ensureChatDir();
  
  const filepath = path.join(CHAT_DIR, getMonthlyFilename());
  
  try {
    const content = await fs.readFile(filepath, 'utf-8');
    const lines = content.trim().split('\n').filter(line => line.length > 0);
    
    const messages: ChatMessage[] = [];
    for (const line of lines) {
      try {
        messages.push(JSON.parse(line) as ChatMessage);
      } catch (parseError) {
        console.warn('Skipping malformed message:', parseError);
      }
    }
    
    console.log(`📖 Loaded all ${messages.length} messages from current month`);
    return messages;
  } catch (error: any) {
    if (error.code === 'ENOENT') {
      return [];
    }
    console.error('Failed to load chat history:', error);
    return [];
  }
}

// Simple token estimation (roughly 1 token per 4 characters)
function estimateTokens(text: string): number {
  return Math.ceil(text.length / 4);
}

// Clear current month's history (for testing/reset)
export async function clearCurrentMonth(): Promise<void> {
  const filepath = path.join(CHAT_DIR, getMonthlyFilename());
  try {
    await fs.unlink(filepath);
    console.log('🗑️ Cleared current month chat history');
  } catch (error: any) {
    if (error.code !== 'ENOENT') {
      console.error('Failed to clear chat history:', error);
    }
  }
}

// Get statistics about chat history
export async function getStats(): Promise<{
  messageCount: number;
  totalTokens: number;
  oldestMessage?: string;
  newestMessage?: string;
}> {
  const messages = await loadAll();
  
  if (messages.length === 0) {
    return { messageCount: 0, totalTokens: 0 };
  }
  
  const totalTokens = messages.reduce((sum, msg) => 
    sum + (msg.metadata?.tokens || estimateTokens(msg.content)), 0
  );
  
  return {
    messageCount: messages.length,
    totalTokens,
    oldestMessage: messages[0].timestamp,
    newestMessage: messages[messages.length - 1].timestamp
  };
}