import { ModelPicker } from '@/components/ModelPicker';
import { ThesisPanel } from '@/components/ThesisPanel';
import { PriceTicker } from '@/components/PriceTicker';
import { ChatDirect } from '@/components/ChatDirect';

export default function Home() {
  return (
    <div className="h-screen bg-background flex flex-col">
      <div className="container mx-auto p-4 flex-1 flex overflow-hidden">
        <div className="flex gap-6 h-full w-full">
          {/* Fixed Left Sidebar */}
          <div className="w-80 flex-shrink-0 flex flex-col space-y-4">
            <div className="mb-6">
              <h1 className="text-2xl font-bold mb-2">Trader Copilot</h1>
              <p className="text-muted-foreground text-sm">
                AI-powered cryptocurrency trading assistant
              </p>
              <p className="text-xs text-green-600 mt-1">
                ✓ Direct OpenAI API (no AI SDK)
              </p>
            </div>
            
            {/* Reordered: Prices → Model → Thesis */}
            <PriceTicker />
            <ModelPicker />
            <ThesisPanel />
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
