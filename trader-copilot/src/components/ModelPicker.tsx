'use client';

import { useSystemStore, MODELS } from '@/lib/system-context';
import { Card } from '@/components/ui/card';

export function ModelPicker() {
  const { modelId, setModelId } = useSystemStore();

  return (
    <Card className="p-4 mb-4">
      <div className="space-y-3">
        <h3 className="font-medium text-sm">AI Model</h3>
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
      </div>
    </Card>
  );
}