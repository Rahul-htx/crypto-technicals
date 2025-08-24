'use client';

import { useState, useEffect } from 'react';
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
  

  useEffect(() => {
    // Load initial snapshot
    loadSnapshot();
  }, []);

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

  const loadSnapshot = async () => {
    try {
      const response = await fetch('/api/snapshot', {
        headers: getAuthHeaders()
      });

      if (response.ok) {
        const snapshot = await response.json();
        // Create a simple hash from the timestamp (Central time)
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
  };

  const refreshSnapshot = async () => {
    setIsRefreshing(true);
    try {
      // Trigger refresh
      await fetch('/api/refresh', {
        method: 'POST',
        headers: getAuthHeaders()
      });

      // Wait a moment then reload
      setTimeout(loadSnapshot, 2000);
    } catch (error) {
      console.error('Failed to refresh snapshot:', error);
    } finally {
      setIsRefreshing(false);
    }
  };

  const getLatestPrices = () => {
    const snapshot = systemCtx.snapshot;
    if (!snapshot) return [];

    const prices: Array<{ coin: string; price: number; change24h: number }> = [];
    
    // Get prices from intraday first, then swing
    const horizonData = snapshot.intraday?.coins || snapshot.swing?.coins;
    if (horizonData) {
      Object.entries(horizonData).forEach(([coin, data]: [string, any]) => {
        if (data.price) {
          prices.push({
            coin: coin.toUpperCase(),
            price: data.price,
            change24h: data.pct_change?.['24h'] || 0
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
          <h3 className="font-medium text-sm">Live Prices</h3>
          <div className="flex items-center space-x-2">
            <Badge variant="outline" className="text-xs">
              {lastSnapshotHash}
            </Badge>
            <Button
              variant="ghost"
              size="sm"
              onClick={refreshSnapshot}
              disabled={isRefreshing}
            >
              <RefreshCw className={`h-3 w-3 ${isRefreshing ? 'animate-spin' : ''}`} />
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
                  <div className={`text-xs ${price.change24h >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {price.change24h >= 0 ? '+' : ''}{price.change24h.toFixed(2)}%
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