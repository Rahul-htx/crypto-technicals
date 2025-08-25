'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { useSystemStore } from '@/lib/system-context';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { RefreshCw, ChevronDown, ChevronUp } from 'lucide-react';
import { getAuthHeaders } from '@/lib/auth';

export function PriceTicker() {
  const { systemCtx, setSnapshot, lastSnapshotHash } = useSystemStore();
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [showViewer, setShowViewer] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<string>('');
  const [clientFormattedTime, setClientFormattedTime] = useState('');
  const [lastStatusHash, setLastStatusHash] = useState<string>('');
  const [autoRefreshEnabled, setAutoRefreshEnabled] = useState(false); // Default to false
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  
  const loadSnapshot = useCallback(async () => {
    try {
      const response = await fetch('/api/snapshot', {
        headers: getAuthHeaders()
      });

      if (response.ok) {
        const snapshot = await response.json();
        const intradayTimestamp = snapshot.intraday?.meta?.run_timestamp;
        const swingTimestamp = snapshot.swing?.meta?.run_timestamp;
        const timestamp = intradayTimestamp || swingTimestamp;
        
        const hash = timestamp ? 
          new Date(timestamp).toLocaleString('en-US', { 
            timeZone: 'America/Chicago',
            hour: 'numeric', 
            minute: '2-digit',
            hour12: false 
          }).replace(':', '') : 
          'unknown';
          
        setSnapshot(snapshot, hash);
      }
    } catch (error) {
      console.error('Failed to load snapshot:', error);
    }
  }, [setSnapshot]);

  useEffect(() => {
    // Fetch initial polling status from backend
    const fetchPollingStatus = async () => {
      try {
        const response = await fetch('/api/control', { headers: getAuthHeaders() });
        if (response.ok) {
          const data = await response.json();
          setAutoRefreshEnabled(data.enabled);
        } else {
          // If the endpoint fails, default to manual for safety
          setAutoRefreshEnabled(false);
        }
      } catch (error) {
        console.error('Failed to fetch polling status:', error);
        setAutoRefreshEnabled(false);
      }
    };

    // Load initial data on mount
    loadSnapshot();
    fetchPollingStatus();
  }, [loadSnapshot]); // This dependency is correct because loadSnapshot is wrapped in useCallback

  useEffect(() => {
    // Update last updated time when snapshot changes
    // Check both intraday and swing meta for run_timestamp
    const intradayTimestamp = systemCtx.snapshot?.intraday?.meta?.run_timestamp;
    const swingTimestamp = systemCtx.snapshot?.swing?.meta?.run_timestamp;
    const timestamp = intradayTimestamp || swingTimestamp;
    
    if (timestamp) {
      setLastUpdated(timestamp);
    }
  }, [systemCtx.snapshot]);

  useEffect(() => {
    // Format timestamp on client-side only to avoid hydration mismatch
    if (lastUpdated) {
      setClientFormattedTime(new Date(lastUpdated).toLocaleString('en-US', { 
        timeZone: 'America/Chicago',
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
      }));
    }
  }, [lastUpdated]);

  // Auto-refresh polling logic
  const checkForUpdates = useCallback(async () => {
    if (!autoRefreshEnabled) return;
    
    try {
      const response = await fetch('/api/status', {
        headers: getAuthHeaders()
      });
      
      if (response.ok) {
        const signal = await response.json();
        const currentHash = signal.hash;
        
        // If we have a new hash and it's different from our last known hash
        if (currentHash && currentHash !== lastStatusHash) {
          console.log('🔄 Auto-refresh: New data detected, updating snapshot...');
          setLastStatusHash(currentHash);
          await loadSnapshot();
        }
      }
    } catch (error) {
      console.error('Auto-refresh status check failed:', error);
    }
  }, [autoRefreshEnabled, lastStatusHash, loadSnapshot]);

  // Set up auto-refresh polling
  useEffect(() => {
    if (autoRefreshEnabled) {
      // Check immediately on enable
      checkForUpdates();
      
      // Then check every 10 seconds
      intervalRef.current = setInterval(checkForUpdates, 10000);
    } else {
      // Clear interval when disabled
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    }

    // Cleanup on unmount
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [autoRefreshEnabled, checkForUpdates]);

  const refreshSnapshot = async () => {
    setIsRefreshing(true);
    try {
      console.log('🔄 Starting manual refresh...');
      
      // Trigger refresh (this now directly executes Python CLI)
      const response = await fetch('/api/refresh', {
        method: 'POST',
        headers: getAuthHeaders()
      });
      
      if (response.ok) {
        console.log('✅ Refresh completed, loading new snapshot...');
        // Reload snapshot immediately since API waits for completion
        await loadSnapshot();
      } else {
        const errorData = await response.json();
        console.error('❌ Refresh failed:', errorData);
        throw new Error(`Refresh failed: ${errorData.message || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Failed to refresh snapshot:', error);
      // Still try to reload in case there was a partial update
      setTimeout(loadSnapshot, 1000);
    } finally {
      setIsRefreshing(false);
    }
  };

  const togglePolling = async () => {
    const newStatus = !autoRefreshEnabled;
    try {
      const response = await fetch('/api/control', {
        method: 'POST',
        headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled: newStatus }),
      });
      if (response.ok) {
        setAutoRefreshEnabled(newStatus);
        console.log(`Backend polling ${newStatus ? 'enabled' : 'disabled'}`);
      }
    } catch (error) {
      console.error('Failed to toggle polling:', error);
    }
  };

  const getLatestPrices = () => {
    const snapshot = systemCtx.snapshot;
    if (!snapshot) return [];

    const prices: Array<{ coin: string; price: number; changeToday: number }> = [];
    
    // Get prices from intraday first, then swing
    const horizonData = snapshot.intraday?.coins || snapshot.swing?.coins;
    if (horizonData) {
      Object.entries(horizonData).forEach(([coin, data]: [string, any]) => {
        if (data.price) {
          prices.push({
            coin: coin.toUpperCase(),
            price: data.price,
            changeToday: data.pct_change?.['24h'] || 0  // Using 24h as proxy for "today"
          });
        }
      });
    }

    return prices.slice(0, 5); // Show top 5
  };

  const prices = getLatestPrices();

  return (
    <Card className="p-4">
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <h3 className="font-medium text-sm">Live Prices</h3>
            {isRefreshing && (
              <span className="text-xs text-blue-600 animate-pulse">
                Fetching fresh data...
              </span>
            )}
          </div>
          <div className="flex items-center space-x-2">
            <Badge variant="outline" className="text-xs">
              {lastSnapshotHash}
            </Badge>
            <Button
              variant={autoRefreshEnabled ? "default" : "outline"}
              size="sm"
              onClick={togglePolling}
              className="text-xs px-2"
              disabled={isRefreshing}
            >
              {autoRefreshEnabled ? '🟢 Auto' : '⭕ Manual'}
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={refreshSnapshot}
              disabled={isRefreshing}
              className={isRefreshing ? 'opacity-75' : ''}
            >
              <RefreshCw className={`h-3 w-3 ${isRefreshing ? 'animate-spin text-blue-600' : ''}`} />
            </Button>
          </div>
        </div>

        {prices.length > 0 ? (
          <div className="space-y-2">
            {prices.map((price) => (
              <div key={price.coin} className="flex justify-between items-center text-sm">
                <span className="font-mono">{price.coin}</span>
                <div className="text-right">
                  <div className="font-mono">
                    ${price.price.toLocaleString(undefined, { maximumFractionDigits: 2 })}
                  </div>
                  <div className={`text-xs ${price.changeToday >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {price.changeToday >= 0 ? '+' : ''}{price.changeToday.toFixed(2)}% 24h
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-muted-foreground text-sm">No price data available</p>
        )}

        {clientFormattedTime && (
          <p className="text-xs text-muted-foreground">
            Updated: {clientFormattedTime} CT
          </p>
        )}

        <Button
          variant="ghost"
          size="sm"
          onClick={() => setShowViewer(!showViewer)}
          className="w-full justify-between"
        >
          <span>Snapshot Viewer</span>
          {showViewer ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
        </Button>

        {showViewer && (
          <div className="mt-3 max-h-60 overflow-auto">
            <pre className="text-xs bg-muted p-3 rounded whitespace-pre-wrap">
              {systemCtx.snapshot ? 
                JSON.stringify(systemCtx.snapshot, null, 2) : 
                'No snapshot data available'
              }
            </pre>
          </div>
        )}
      </div>
    </Card>
  );
}