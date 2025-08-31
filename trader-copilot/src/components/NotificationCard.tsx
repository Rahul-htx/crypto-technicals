'use client';

import React from 'react';
import { SystemNotification } from '@/types/notifications';
import { Badge } from '@/components/ui/badge';

interface NotificationCardProps {
  notification: SystemNotification;
  className?: string;
}

export function NotificationCard({ notification, className = '' }: NotificationCardProps) {
  // Format timestamp to CT timezone in MMM DD HH:MM AM/PM format
  const formatTimestamp = (isoString: string): string => {
    try {
      const date = new Date(isoString);
      return date.toLocaleString('en-US', {
        timeZone: 'America/Chicago',
        month: 'short',
        day: 'numeric', 
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
      }) + ' CT';
    } catch {
      return isoString; // Fallback
    }
  };

  // Determine styling based on severity
  const getSeverityStyles = () => {
    if (notification.severity === 'HIGH') {
      return {
        containerClass: 'bg-yellow-100 text-yellow-800 border-l-4 border-yellow-500 dark:bg-yellow-900/20 dark:text-yellow-300 dark:border-yellow-400',
        icon: '⚡',
        badgeVariant: 'default' as const
      };
    } else {
      return {
        containerClass: 'bg-muted text-muted-foreground border-l-4 border-muted dark:bg-muted/50',
        icon: '🔍',
        badgeVariant: 'outline' as const
      };
    }
  };

  const { containerClass, icon, badgeVariant } = getSeverityStyles();

  return (
    <div 
      className={`rounded-md py-2 px-3 text-xs font-medium mb-2 ${containerClass} ${className}`}
      role="status"
      aria-label={`System notification: ${notification.description}`}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-start gap-2 flex-1 min-w-0">
          {/* Leading icon */}
          <span className="text-sm flex-shrink-0 mt-0.5" aria-hidden="true">
            {icon}
          </span>
          
          {/* Main content */}
          <div className="flex-1 min-w-0">
            <div className="font-medium truncate">
              {notification.description}
            </div>
            
            {/* Timestamp and meta info */}
            <div className="flex items-center gap-2 mt-1 text-xs opacity-75">
              <span>{formatTimestamp(notification.timestamp)}</span>
              
              {notification.meta?.tool_name && (
                <>
                  <span>•</span>
                  <span className="font-mono">{notification.meta.tool_name}</span>
                </>
              )}
              
              {notification.meta?.token_delta && (
                <>
                  <span>•</span>
                  <span>{notification.meta.token_delta} tokens</span>
                </>
              )}
            </div>
          </div>
        </div>
        
        {/* Severity badge */}
        <Badge 
          variant={badgeVariant} 
          className="text-xs flex-shrink-0 ml-2"
        >
          {notification.severity}
        </Badge>
      </div>
      
      {/* Optional action details for market intelligence updates */}
      {notification.meta?.action && notification.meta.tool_name === 'update_market_intel' && (
        <div className="mt-1 text-xs opacity-60">
          Action: {notification.meta.action}
          {notification.meta.details?.pruned_items !== undefined && 
            ` (${notification.meta.details.pruned_items} items pruned)`
          }
        </div>
      )}
    </div>
  );
}

// Collapsible notification list component for managing the 5-item limit
interface NotificationListProps {
  notifications: SystemNotification[];
  className?: string;
}

export function NotificationList({ notifications, className = '' }: NotificationListProps) {
  const [showAll, setShowAll] = React.useState(false);
  
  // Show only the 5 most recent notifications by default
  const visibleNotifications = showAll ? notifications : notifications.slice(-5);
  const hasMore = notifications.length > 5;
  
  if (notifications.length === 0) {
    return null;
  }
  
  return (
    <div className={`space-y-1 ${className}`}>
      {visibleNotifications.map((notification) => (
        <NotificationCard 
          key={notification.id} 
          notification={notification}
        />
      ))}
      
      {hasMore && !showAll && (
        <button
          onClick={() => setShowAll(true)}
          className="text-xs text-muted-foreground hover:text-foreground transition-colors py-1 px-2 rounded"
        >
          Show {notifications.length - 5} more notifications...
        </button>
      )}
      
      {showAll && hasMore && (
        <button
          onClick={() => setShowAll(false)}
          className="text-xs text-muted-foreground hover:text-foreground transition-colors py-1 px-2 rounded"
        >
          Show less
        </button>
      )}
    </div>
  );
}

