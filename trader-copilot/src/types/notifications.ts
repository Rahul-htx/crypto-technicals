// Notification system types for Trader-Copilot chat UI

export type NotificationSeverity = 'HIGH' | 'NORMAL';

export interface SystemNotification {
  id: string;
  timestamp: string; // ISO string
  severity: NotificationSeverity;
  description: string;
  meta?: {
    tool_name: string;
    action?: string;
    token_delta?: number;
    details?: Record<string, any>;
  };
}

export interface NotificationTrigger {
  tool_name: string;
  severity: NotificationSeverity;
  conditions?: string[]; // For actions like add_diff, promote_to_core, etc.
  description_template: string;
}

// Notification triggers configuration
export const NOTIFICATION_TRIGGERS: NotificationTrigger[] = [
  // HIGH severity - data mutations
  {
    tool_name: 'update_thesis',
    severity: 'HIGH',
    description_template: 'Investment thesis updated'
  },
  {
    tool_name: 'update_market_intel',
    severity: 'HIGH',
    conditions: ['add_diff', 'promote_to_core', 'prune_stale', 'run_curation'],
    description_template: 'Market intelligence updated'
  },
  
  // NORMAL severity - read operations
  {
    tool_name: 'get_coin_snapshot',
    severity: 'NORMAL',
    description_template: 'Retrieved coin data snapshot'
  },
  {
    tool_name: 'get_market_snapshot',
    severity: 'NORMAL', 
    description_template: 'Retrieved market overview data'
  },
  {
    tool_name: 'get_full_snapshot',
    severity: 'NORMAL',
    description_template: 'Retrieved full market snapshot'
  },
  {
    tool_name: 'get_market_intel',
    severity: 'NORMAL',
    description_template: 'Retrieved market intelligence data'
  }
];

// Helper function to get human-friendly descriptions
export function getNotificationDescription(
  toolName: string, 
  action?: string, 
  result?: any
): string {
  const trigger = NOTIFICATION_TRIGGERS.find(t => t.tool_name === toolName);
  if (!trigger) return `${toolName} executed`;
  
  // Customize descriptions based on tool and action
  switch (toolName) {
    case 'update_thesis':
      return 'Investment thesis updated';
      
    case 'update_market_intel':
      switch (action) {
        case 'add_diff':
          return 'Added new market development';
        case 'promote_to_core':
          return 'Promoted development to core facts';
        case 'prune_stale':
          const pruned = result?.details?.pruned_items || 0;
          return `Pruned ${pruned} stale market facts`;
        case 'run_curation':
          return 'Ran market intelligence curation';
        default:
          return 'Market intelligence updated';
      }
      
    case 'get_coin_snapshot':
      const coin = result?.coin || 'coin';
      return `Retrieved ${coin.toUpperCase()} data`;
      
    case 'get_market_snapshot':
      return 'Retrieved market overview';
      
    case 'get_full_snapshot':
      return 'Retrieved complete market data';
      
    case 'get_market_intel':
      return 'Retrieved market intelligence';
      
    default:
      return trigger.description_template;
  }
}

// Helper function to check if a tool call should trigger a notification
export function shouldTriggerNotification(toolName: string, action?: string): NotificationSeverity | null {
  const trigger = NOTIFICATION_TRIGGERS.find(t => t.tool_name === toolName);
  if (!trigger) return null;
  
  // Check conditions if they exist
  if (trigger.conditions && action) {
    if (!trigger.conditions.includes(action)) return null;
  }
  
  return trigger.severity;
}