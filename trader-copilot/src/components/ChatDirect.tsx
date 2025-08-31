'use client';

import { useState, useRef, useEffect } from 'react';
import { useSystemStore, MODELS } from '@/lib/system-context';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Send, Bot, User, Loader2, ExternalLink } from 'lucide-react';
import { getAuthHeaders } from '@/lib/auth';
import { SystemNotification } from '@/types/notifications';
import { NotificationCard } from '@/components/NotificationCard';

interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
  toolCalls?: any[];
  timestamp?: string;
}

interface ToolCallEvent {
  type: 'tool_call';
  name: string;
  args: any;
  result: any;
}

interface ProgressEvent {
  type: 'progress';
  stage: string;
  message: string;
  section?: string;
}

// Helper function to format timestamps in CT timezone
function formatTimestamp(date: Date): string {
  return date.toLocaleString('en-US', {
    timeZone: 'America/Chicago',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  });
}

// Helper function to format content with clickable links and basic markdown
function formatContent(content: string) {
  // First, let's process the content as a single unit
  let processedContent = content;
  
  // Handle headers first
  processedContent = processedContent.replace(/^# (.+)$/gm, '<h1 class="text-lg font-bold mt-4 mb-3 first:mt-0">$1</h1>');
  processedContent = processedContent.replace(/^## (.+)$/gm, '<h2 class="text-base font-semibold mt-3 mb-2">$1</h2>');
  
  // Handle bold text
  processedContent = processedContent.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold">$1</strong>');
  
  // Handle italic text  
  processedContent = processedContent.replace(/\*(.*?)\*/g, '<em class="italic">$1</em>');
  
  // Convert markdown links to HTML links
  processedContent = processedContent.replace(
    /\[([^\]]+)\]\((https?:\/\/[^\)]+)\)/g, 
    '<a href="$2" target="_blank" rel="noopener noreferrer" class="inline-flex items-center gap-1 text-blue-600 hover:text-blue-800 underline">$1 <svg class="h-3 w-3 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg></a>'
  );
  
  // Handle paragraphs - split by double newlines
  const paragraphs = processedContent.split(/\n\s*\n/);
  const formattedParagraphs = paragraphs.map((para, index) => {
    const trimmed = para.trim();
    if (!trimmed) return '';
    
    // If it's already a header, return as-is
    if (trimmed.startsWith('<h1') || trimmed.startsWith('<h2')) {
      return trimmed;
    }
    
    // Wrap in paragraph tags with proper spacing
    return `<p class="mb-3 leading-relaxed">${trimmed}</p>`;
  }).filter(Boolean).join('');
  
  return (
    <div 
      className="space-y-0" 
      dangerouslySetInnerHTML={{ __html: formattedParagraphs }}
    />
  );
}

export function ChatDirect() {
  const { modelId, enableWebSearch, setModelId, setEnableWebSearch } = useSystemStore();
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [streamingContent, setStreamingContent] = useState('');
  const [progressState, setProgressState] = useState<ProgressEvent | null>(null);
  const [currentSection, setCurrentSection] = useState<string>('');
  const [historyLoaded, setHistoryLoaded] = useState(false);
  const [notifications, setNotifications] = useState<SystemNotification[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Function to fetch notifications after tool calls
  const fetchNotifications = async () => {
    try {
      console.log('🔍 Fetching notifications...');
      const response = await fetch('/api/notifications', {
        headers: getAuthHeaders()
      });
      
      console.log('📡 Notification response status:', response.status);
      const data = await response.json();
      console.log('📡 Notification response data:', data);
      
      const { notifications } = data;
      
      if (notifications && notifications.length > 0) {
        console.log('📢 Fetched notifications:', notifications.length, notifications);
        setNotifications(prev => {
          console.log('📢 Previous notifications:', prev.length);
          const updated = [...prev, ...notifications];
          console.log('📢 Updated notifications:', updated.length);
          return updated;
        });
      } else {
        console.log('📢 No notifications to fetch');
      }
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
    }
  };

  // Helper function to create timeline with interleaved notifications
  const createTimeline = () => {
    const timeline: Array<{ type: 'message' | 'notifications'; data: any; timestamp: string }> = [];
    
    // Debug logging
    console.log('Creating timeline with:', { 
      messageCount: messages.length, 
      notificationCount: notifications.length,
      notifications: notifications.map(n => ({ id: n.id, timestamp: n.timestamp, description: n.description }))
    });
    
    // Add all messages to timeline
    messages.forEach((message, index) => {
      timeline.push({
        type: 'message',
        data: { message, index },
        timestamp: message.timestamp || new Date().toISOString()
      });
      
      // If this is the LAST assistant message, show ALL pending notifications after it
      // This is simpler and more reliable than trying to match timestamps
      if (message.role === 'assistant' && index === messages.length - 1 && notifications.length > 0) {
        timeline.push({
          type: 'notifications',
          data: notifications,
          timestamp: notifications[0].timestamp
        });
        console.log('Added notifications after last assistant message:', notifications.length);
      }
    });
    
    // Sort timeline by timestamp
    timeline.sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
    
    return timeline;
  };

  // Load chat history on mount
  useEffect(() => {
    async function loadHistory() {
      try {
        const response = await fetch('/api/chat-history?mode=context', {
          headers: getAuthHeaders()
        });
        
        if (response.ok) {
          const data = await response.json();
          if (data.messages && data.messages.length > 0) {
            setMessages(data.messages);
            console.log(`📖 Loaded ${data.messages.length} messages from history`);
          }
        }
      } catch (error) {
        console.error('Failed to load chat history:', error);
      } finally {
        setHistoryLoaded(true);
      }
    }
    
    loadHistory();
  }, []); // Only run once on mount

  // Auto-scroll to bottom whenever messages or streaming content changes
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingContent, progressState]);

  // Also ensure scroll to bottom when progress state updates
  useEffect(() => {
    if (progressState || streamingContent) {
      setTimeout(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
      }, 100); // Small delay to ensure DOM updates
    }
  }, [progressState, streamingContent]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date().toISOString()
    };

    setInput('');
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setStreamingContent('');
    setProgressState(null);
    setCurrentSection('');

    // Save user message to history
    try {
      await fetch('/api/chat-history', {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          role: 'user',
          content: userMessage.content,
          metadata: { tokens: Math.ceil(userMessage.content.length / 4) }
        })
      });
    } catch (error) {
      console.error('Failed to save user message:', error);
    }

    try {
      const response = await fetch('/api/chat-direct', {
        method: 'POST',
        headers: {
          ...getAuthHeaders(),
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: [...messages, userMessage],
          model: modelId,
          enableWebSearch: enableWebSearch
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error('No response body');

      const decoder = new TextDecoder();
      let buffer = '';
      let currentContent = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data.trim() === '') continue;

            try {
              const parsed = JSON.parse(data);
              
              if (parsed.type === 'content') {
                currentContent += parsed.content;
                setStreamingContent(currentContent);
              } else if (parsed.type === 'progress') {
                setProgressState(parsed as ProgressEvent);
                if (parsed.section) {
                  setCurrentSection(parsed.section);
                }
              } else if (parsed.type === 'tool_call') {
                // Show tool call in UI (optional)
                console.log('Tool called:', parsed.name, parsed.args);
                
                // Auto-refresh thesis if it was updated
                if (parsed.name === 'update_thesis' && parsed.result?.success) {
                  // Trigger thesis reload in ThesisPanel
                  window.dispatchEvent(new CustomEvent('thesisUpdated'));
                }
              } else if (parsed.type === 'error') {
                // Handle error from deep research
                setMessages(prev => [...prev, {
                  role: 'assistant',
                  content: `Error: ${parsed.error}`,
                  timestamp: new Date().toISOString()
                }]);
                setProgressState(null);
                break;
              } else if (parsed.type === 'done') {
                // Finalize the message
                if (currentContent) {
                  const assistantMessage = {
                    role: 'assistant' as const,
                    content: currentContent,
                    timestamp: new Date().toISOString()
                  };
                  setMessages(prev => [...prev, assistantMessage]);
                  setStreamingContent('');
                  
                  // Save assistant message to history
                  try {
                    await fetch('/api/chat-history', {
                      method: 'POST',
                      headers: getAuthHeaders(),
                      body: JSON.stringify({
                        role: 'assistant',
                        content: currentContent,
                        model: modelId,
                        metadata: { tokens: Math.ceil(currentContent.length / 4) }
                      })
                    });
                  } catch (error) {
                    console.error('Failed to save assistant message:', error);
                  }
                  
                  // Fetch notifications after assistant message is complete
                  await fetchNotifications();
                }
                setProgressState(null);
                break;
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e);
            }
          }
        }
      }
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error while processing your request. Please try again.',
        timestamp: new Date().toISOString()
      }]);
    } finally {
      setIsLoading(false);
      setProgressState(null);
    }
  };

  return (
    <Card className="flex flex-col h-full">
      <div className="p-4 border-b flex-shrink-0">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">CryptoCortex Chat</h2>
          <div className="flex items-center gap-3">
            {/* Model Picker */}
            <div className="flex items-center space-x-2">
              <label className="text-sm font-medium text-muted-foreground">Model:</label>
              <select
                value={modelId}
                onChange={(e) => setModelId(e.target.value)}
                className="bg-background border border-border rounded px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              >
                {Object.entries(MODELS).map(([id, label]) => (
                  <option key={id} value={id}>
                    {label}
                  </option>
                ))}
              </select>
            </div>
            
            {/* Web Search Toggle */}
            {['o3', 'o3-pro', 'o4-mini', 'gpt-5'].includes(modelId) && (
              <div className="flex items-center space-x-2">
                <label className="flex items-center space-x-2 cursor-pointer text-sm">
                  <input
                    type="checkbox"
                    checked={enableWebSearch}
                    onChange={(e) => setEnableWebSearch(e.target.checked)}
                    className="h-4 w-4"
                  />
                  <span>Web Search</span>
                </label>
              </div>
            )}
            
            <Badge variant="outline" className="text-xs text-green-600">
              Direct OpenAI API
            </Badge>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4 min-h-0">
        {!historyLoaded ? (
          <div className="text-center text-muted-foreground py-8">
            <Loader2 className="h-8 w-8 mx-auto mb-2 animate-spin opacity-50" />
            <p className="text-sm">Loading chat history...</p>
          </div>
        ) : messages.length === 0 && !streamingContent ? (
          <div className="text-center text-muted-foreground py-8">
            <Bot className="h-12 w-12 mx-auto mb-2 opacity-50" />
            <p className="text-sm">
              Ask me about cryptocurrency prices, market analysis, or trading strategies.
            </p>
            <p className="text-xs mt-2">
              Using direct OpenAI API with persistent chat history
            </p>
          </div>
        ) : null}

        {createTimeline().map((item, timelineIndex) => {
          if (item.type === 'message') {
            const { message, index } = item.data;
            return (
              <div
                key={`message-${index}`}
                className={`flex gap-3 ${
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                <div
                  className={`flex gap-3 max-w-[80%] ${
                    message.role === 'user' ? 'flex-row-reverse' : 'flex-row'
                  }`}
                >
                  <div className="flex-shrink-0">
                    {message.role === 'user' ? (
                      <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center">
                        <User className="h-4 w-4 text-primary-foreground" />
                      </div>
                    ) : (
                      <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center">
                        <Bot className="h-4 w-4" />
                      </div>
                    )}
                  </div>
                  <div
                    className={`rounded-lg px-4 py-2 ${
                      message.role === 'user'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted'
                    }`}
                  >
                    <div>
                  {message.role === 'user' ? (
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                  ) : (
                    <div className="text-sm">
                      {formatContent(message.content)}
                    </div>
                  )}
                  {message.timestamp && (
                    <p className="text-xs text-muted-foreground mt-2 opacity-70">
                      {formatTimestamp(new Date(message.timestamp))} CT
                    </p>
                  )}
                </div>
              </div>
            </div>
          </div>
            );
          } else if (item.type === 'notifications') {
            // Render notification cards
            const notificationList = item.data as SystemNotification[];
            return (
              <div key={`notifications-${timelineIndex}`} className="max-w-full px-4">
                {notificationList.map(notification => (
                  <NotificationCard 
                    key={notification.id} 
                    notification={notification}
                    className="mb-2"
                  />
                ))}
              </div>
            );
          }
          return null;
        })}

        {streamingContent && (
          <div className="flex gap-3 justify-start">
            <div className="flex gap-3 max-w-[80%]">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center">
                  <Bot className="h-4 w-4" />
                </div>
              </div>
              <div className="rounded-lg px-4 py-2 bg-muted">
                <div className="text-sm">
                  {formatContent(streamingContent)}
                </div>
              </div>
            </div>
          </div>
        )}

        {progressState && (
          <div className="flex gap-3 justify-start">
            <div className="flex gap-3 max-w-[80%]">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                  <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
                </div>
              </div>
              <div className="rounded-lg px-4 py-2 bg-blue-50 border border-blue-200">
                <div className="space-y-1">
                  <p className="text-sm font-medium text-blue-900">{progressState.message}</p>
                  {currentSection && (
                    <Badge variant="outline" className="text-xs text-blue-700 bg-blue-100">
                      {currentSection}
                    </Badge>
                  )}
                  <p className="text-xs text-blue-600 capitalize">
                    Stage: {progressState.stage.replace('_', ' ')}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {isLoading && !streamingContent && !progressState && (
          <div className="flex gap-3 justify-start">
            <div className="flex gap-3 max-w-[80%]">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center">
                  <Bot className="h-4 w-4" />
                </div>
              </div>
              <div className="rounded-lg px-4 py-2 bg-muted">
                <Loader2 className="h-4 w-4 animate-spin" />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <Separator />

      <form onSubmit={handleSubmit} className="p-4 flex-shrink-0">
        <div className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about crypto prices, market analysis..."
            disabled={isLoading}
            className="flex-1"
            autoComplete="off"
          />
          <Button type="submit" disabled={isLoading || !input.trim()}>
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
      </form>
    </Card>
  );
}