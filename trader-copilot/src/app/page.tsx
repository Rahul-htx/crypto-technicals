import { ModelPicker } from '@/components/ModelPicker';
import { ThesisPanel } from '@/components/ThesisPanel';
import { PriceTicker } from '@/components/PriceTicker';
import { Chat } from '@/components/Chat';

export default function Home() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto p-4">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-screen">
          {/* Left Sidebar */}
          <div className="lg:col-span-1 space-y-4 max-h-screen overflow-y-auto">
            <div className="mb-6">
              <h1 className="text-2xl font-bold mb-2">Trader Copilot</h1>
              <p className="text-muted-foreground text-sm">
                AI-powered cryptocurrency trading assistant
              </p>
            </div>
            
            <ModelPicker />
            <ThesisPanel />
            <PriceTicker />
          </div>

          {/* Right Chat Area */}
          <div className="lg:col-span-3 h-full flex flex-col">
            <Chat />
          </div>
        </div>
      </div>
    </div>
  );
}
