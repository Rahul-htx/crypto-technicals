'use client';

import { ThesisPanel } from '@/components/ThesisPanel';
import { PriceTicker } from '@/components/PriceTicker';
import { ChatDirect } from '@/components/ChatDirect';
import { MarketIntelPanel } from '@/components/MarketIntelPanel';
import { CollapsibleSection } from '@/components/ui/collapsible-section';
import { useSystemStore } from '@/lib/system-context';
import { useState } from 'react';
import { Badge } from '@/components/ui/badge';

export default function Home() {
  const [expandedSection, setExpandedSection] = useState<string>('prices'); // Only one section expanded at a time
  const [marketIntelPreview, setMarketIntelPreview] = useState<string>('Loading...');
  
  const handleSectionToggle = (section: string) => {
    setExpandedSection(expandedSection === section ? '' : section);
  };

  return (
    <div className="h-screen bg-background flex flex-col">
      {/* Header Bar */}
      <div className="border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 py-3 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold">CryptoCortex</h1>
            <p className="text-xs text-muted-foreground">
              AI-powered cryptocurrency trading assistant
            </p>
          </div>
          
          <div className="flex items-center space-x-4">
            <Badge variant="outline" className="text-xs text-green-600">
              CryptoCortex AI Assistant
            </Badge>
          </div>
        </div>
      </div>
      
      {/* Main Content */}
      <div className="container mx-auto p-4 flex-1 flex overflow-hidden">
        <div className="flex gap-6 h-full w-full">
          {/* Fixed Left Sidebar */}
          <div className="w-96 flex-shrink-0 flex flex-col space-y-4 overflow-y-auto max-h-full">
            {/* Live Prices - Keep existing PriceTicker logic */}
            <PriceTicker />
            
            {/* Investment Thesis */}
            <CollapsibleSection
              title="Investment Thesis"
              description="Current trading strategy and market outlook"
              isExpanded={expandedSection === 'thesis'}
              onExpandedChange={() => handleSectionToggle('thesis')}
              showInfo={true}
              infoTooltip="View and update your current investment thesis"
            >
              <ThesisPanel />
            </CollapsibleSection>
            
            {/* Market Intelligence */}
            <CollapsibleSection
              title="Market Intelligence"
              description="Core facts and recent market developments"
              isExpanded={expandedSection === 'market-intel'}
              onExpandedChange={() => handleSectionToggle('market-intel')}
              showInfo={true}
              infoTooltip="Hierarchical market intelligence: stable facts + recent updates"
              collapsedPreview={marketIntelPreview}
            >
              <MarketIntelPanel onPreviewChange={setMarketIntelPreview} />
            </CollapsibleSection>
          </div>

          {/* Right Chat Area - Scrollable */}
          <div className="flex-1 flex flex-col min-w-0">
            <ChatDirect />
          </div>
        </div>
      </div>
    </div>
  );
}
