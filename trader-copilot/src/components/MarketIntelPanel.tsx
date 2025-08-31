'use client';

import { useState, useEffect } from 'react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { RefreshCw } from 'lucide-react';
import { getAuthHeaders } from '@/lib/auth';

interface MarketIntelItem {
  id: string;
  content: string;
  category?: string;
  last_verified?: string;
  reference_count?: number;
  created_at?: string;
  hit_count?: number;
  confidence?: number;
  promotion_eligible?: boolean;
  source?: string;
}

interface MarketIntelData {
  version: number;
  last_updated: string;
  updated_by: string;
  core: {
    last_verified: string;
    items: MarketIntelItem[];
  };
  diff: {
    items: MarketIntelItem[];
  };
  metadata: {
    core_token_count: number;
    diff_token_count: number;
    total_token_count: number;
    last_curation_run?: string;
    next_curation_due?: string;
  };
}

interface MarketIntelPanelProps {
  onPreviewChange?: (preview: string) => void;
}

export function MarketIntelPanel({ onPreviewChange }: MarketIntelPanelProps) {
  const [marketIntel, setMarketIntel] = useState<MarketIntelData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<string>('');

  const loadMarketIntel = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/market-intel', {
        headers: getAuthHeaders()
      });

      if (response.ok) {
        const data = await response.json();
        setMarketIntel(data);
        setLastUpdated(new Date(data.last_updated).toLocaleString('en-US', {
          timeZone: 'America/Chicago',
          month: 'short',
          day: 'numeric',
          hour: 'numeric',
          minute: '2-digit',
          hour12: true
        }));
        
        // Update collapsed preview
        if (onPreviewChange) {
          const coreCount = data.core.items.length;
          const diffCount = data.diff.items.length;
          onPreviewChange(`${coreCount} Core, ${diffCount} Recent`);
        }
      } else {
        console.error('Failed to load market intelligence');
      }
    } catch (error) {
      console.error('Error loading market intelligence:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadMarketIntel();
  }, []);

  const getCollapsedPreview = () => {
    if (!marketIntel) return 'Loading...';
    const coreCount = marketIntel.core.items.length;
    const diffCount = marketIntel.diff.items.length;
    return `${coreCount} Core, ${diffCount} Recent`;
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  const getCategoryBadgeVariant = (category: string) => {
    switch (category) {
      case 'principle': return 'default';
      case 'market_structure': return 'secondary';
      case 'macro': return 'outline';
      case 'regulatory': return 'destructive';
      default: return 'outline';
    }
  };

  return (
    <div className="space-y-4">
      {/* Header with refresh button */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          {lastUpdated && (
            <span className="text-xs text-muted-foreground">
              Updated: {lastUpdated} CT
            </span>
          )}
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={loadMarketIntel}
          disabled={isLoading}
        >
          <RefreshCw className={`h-3 w-3 ${isLoading ? 'animate-spin' : ''}`} />
        </Button>
      </div>

      {marketIntel ? (
        <div className="space-y-4">
          {/* Core Facts Section */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-medium text-green-700 dark:text-green-400">
                Stable Market Facts (Core)
              </h4>
              <Badge variant="outline" className="text-xs">
                {marketIntel.core.items.length} items
              </Badge>
            </div>
            <div className="space-y-2">
              {marketIntel.core.items.map((item) => (
                <div key={item.id} className="text-sm">
                  <div className="flex items-start justify-between gap-2">
                    <span className="flex-1">• {item.content}</span>
                    {item.category && (
                      <Badge 
                        variant={getCategoryBadgeVariant(item.category)}
                        className="text-xs shrink-0"
                      >
                        {item.category}
                      </Badge>
                    )}
                  </div>
                  {item.reference_count !== undefined && (
                    <div className="text-xs text-muted-foreground ml-2 mt-1">
                      Referenced {item.reference_count} times
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Recent Updates Section */}
          {marketIntel.diff.items.length > 0 && (
            <div>
              <div className="flex items-center justify-between mb-2">
                <h4 className="text-sm font-medium text-blue-700 dark:text-blue-400">
                  Recent Developments (Diff)
                </h4>
                <Badge variant="outline" className="text-xs">
                  {marketIntel.diff.items.length} updates
                </Badge>
              </div>
              <div className="space-y-2">
                {marketIntel.diff.items.map((item) => (
                  <div key={item.id} className="text-sm">
                    <div className="flex items-start justify-between gap-2">
                      <span className="flex-1">• {item.content}</span>
                      {item.confidence !== undefined && (
                        <Badge 
                          variant={item.confidence >= 0.8 ? "default" : "secondary"}
                          className="text-xs shrink-0"
                        >
                          {Math.round(item.confidence * 100)}%
                        </Badge>
                      )}
                    </div>
                    <div className="text-xs text-muted-foreground ml-2 mt-1 flex justify-between">
                      <span>
                        {item.created_at && formatTimestamp(item.created_at)}
                        {item.hit_count !== undefined && ` • ${item.hit_count} hits`}
                      </span>
                      {item.promotion_eligible && (
                        <span className="text-green-600 dark:text-green-400">
                          ↑ Promotion eligible
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Token Usage */}
          <div className="flex justify-between items-center text-xs text-muted-foreground pt-2 border-t border-muted">
            <span>
              Token usage: {marketIntel.metadata.total_token_count} 
              <span className="text-muted-foreground/60"> / 10,000</span>
            </span>
            <span>
              Core: {marketIntel.metadata.core_token_count} | 
              Diff: {marketIntel.metadata.diff_token_count}
            </span>
          </div>
        </div>
      ) : (
        <div className="text-sm text-muted-foreground">
          {isLoading ? 'Loading market intelligence...' : 'No market intelligence available'}
        </div>
      )}
    </div>
  );
}