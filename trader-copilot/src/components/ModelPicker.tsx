'use client';

import { useSystemStore, MODELS } from '@/lib/system-context';
import { Card } from '@/components/ui/card';

interface ModelPickerProps {
  hideWebSearch?: boolean;
}

interface HeaderModelPickerProps {
  compact?: boolean;
}

export function ModelPicker({ hideWebSearch = false }: ModelPickerProps) {
  const { modelId, setModelId, enableWebSearch, setEnableWebSearch } = useSystemStore();
  
  // Check if current model supports web search
  const webSearchCapableModels = ['o3', 'o3-pro', 'o4-mini', 'gpt-5'];
  const currentModelSupportsWebSearch = webSearchCapableModels.includes(modelId);

  return (
    <div className="space-y-3">
      <div className="space-y-2">
        {Object.entries(MODELS).map(([id, label]) => (
          <label
            key={id}
            className="flex items-center space-x-2 cursor-pointer hover:bg-muted/50 p-2 rounded"
          >
            <input
              type="radio"
              value={id}
              checked={modelId === id}
              onChange={(e) => setModelId(e.target.value)}
              className="h-4 w-4"
            />
            <span className="text-sm">{label}</span>
          </label>
        ))}
      </div>
      
      {/* Web Search Option - only show if not hidden and model supports it */}
      {!hideWebSearch && currentModelSupportsWebSearch && (
        <div className="pt-2 border-t border-muted">
          <label className="flex items-center space-x-2 cursor-pointer hover:bg-muted/30 p-2 rounded">
            <input
              type="checkbox"
              checked={enableWebSearch}
              onChange={(e) => setEnableWebSearch(e.target.checked)}
              className="h-4 w-4"
            />
            <div className="flex flex-col">
              <span className="text-sm font-medium">Enable Web Search</span>
              <span className="text-xs text-muted-foreground">
                Search the web for current information
              </span>
            </div>
          </label>
        </div>
      )}
    </div>
  );
}

// Compact header version
export function HeaderModelPicker({ compact = true }: HeaderModelPickerProps) {
  const { modelId, setModelId } = useSystemStore();

  return (
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
  );
}