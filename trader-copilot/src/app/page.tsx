'use client';

import { ModelPicker } from '@/components/ModelPicker';
import { ThesisPanel } from '@/components/ThesisPanel';
import { PriceTicker } from '@/components/PriceTicker';
import { ChatDirect } from '@/components/ChatDirect';
import { MarketIntelPanel } from '@/components/MarketIntelPanel';
import { CollapsibleSection } from '@/components/ui/collapsible-section';
import { useSystemStore, MODELS } from '@/lib/system-context';
import { useState } from 'react';
import { Badge } from '@/components/ui/badge';

export default function Home() {
  const { enableWebSearch, setEnableWebSearch, modelId } = useSystemStore();
  const [expandedSection, setExpandedSection] = useState<string>('prices'); // Only one section expanded at a time
  const [marketIntelPreview, setMarketIntelPreview] = useState<string>('Loading...');
  
  // Check if current model supports web search
  const webSearchCapableModels = ['o3', 'o3-pro', 'o4-mini', 'gpt-5'];
  const currentModelSupportsWebSearch = webSearchCapableModels.includes(modelId);
  
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
            {/* Web Search Toggle */}
            {currentModelSupportsWebSearch && (
              <div className="flex items-center space-x-2">
                <label className="flex items-center space-x-2 cursor-pointer text-sm">
                  <input
                    type="checkbox"
                    checked={enableWebSearch}
                    onChange={(e) => setEnableWebSearch(e.target.checked)}
                    className="h-4 w-4"
                  />
                  <span>Web Search</span>
                  <Badge variant="outline" className="text-xs">
                    {MODELS[modelId as keyof typeof MODELS]}
                  </Badge>
                </label>
              </div>
            )}
            
            <Badge variant="outline" className="text-xs text-green-600">
              Direct OpenAI API
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
            
            {/* AI Model Selection */}
            <CollapsibleSection
              title="AI Model"
              description="Select the AI model for analysis"
              isExpanded={expandedSection === 'model'}
              onExpandedChange={() => handleSectionToggle('model')}
              showInfo={true}
              infoTooltip="Choose between different AI models with varying capabilities"
              collapsedPreview={MODELS[modelId as keyof typeof MODELS]}
            >
              <ModelPicker hideWebSearch={true} />
            </CollapsibleSection>
            
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
