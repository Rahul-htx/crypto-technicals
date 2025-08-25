import { create } from 'zustand';
import { Snapshot } from './kv';

export interface SystemContext {
  thesis: string;
  snapshot: Snapshot | null;
  updatedAt: string;
  updatedBy: string;
}

export interface SystemState {
  modelId: string;
  systemCtx: SystemContext;
  lastSnapshotHash: string;
  isLoading: boolean;
  enableWebSearch: boolean;
  setModelId: (modelId: string) => void;
  setSnapshot: (snapshot: Snapshot | null, hash: string) => void;
  setThesis: (thesis: string, updatedBy: string) => void;
  setLoading: (loading: boolean) => void;
  setEnableWebSearch: (enabled: boolean) => void;
}

const MODELS = {
  'o3': 'o3',
  'o3-deep-research': 'o3-deep-research', 
  'o4-mini-deep-research': 'o4-mini-deep-research',
  'gpt-5': 'gpt-5',
} as const;

export const useSystemStore = create<SystemState>((set, get) => ({
  modelId: 'o3', // Default as per spec
  systemCtx: {
    thesis: '',
    snapshot: null,
    updatedAt: new Date().toISOString(),
    updatedBy: 'system'
  },
  lastSnapshotHash: '',
  isLoading: false,
  enableWebSearch: false, // Default to NO web search

  setModelId: (modelId: string) => {
    set({ modelId });
    // Persist to localStorage
    if (typeof window !== 'undefined') {
      localStorage.setItem('trader-copilot-model', modelId);
    }
  },

  setSnapshot: (snapshot: Snapshot | null, hash: string) => {
    set(state => ({
      systemCtx: { ...state.systemCtx, snapshot },
      lastSnapshotHash: hash
    }));
  },

  setThesis: (thesis: string, updatedBy: string) => {
    set(state => ({
      systemCtx: {
        ...state.systemCtx,
        thesis,
        updatedAt: new Date().toISOString(),
        updatedBy
      }
    }));
  },

  setLoading: (isLoading: boolean) => {
    set({ isLoading });
  },

  setEnableWebSearch: (enableWebSearch: boolean) => {
    set({ enableWebSearch });
    // Persist to localStorage
    if (typeof window !== 'undefined') {
      localStorage.setItem('trader-copilot-websearch', enableWebSearch.toString());
    }
  }
}));

// Initialize model and web search preference from localStorage on client side
if (typeof window !== 'undefined') {
  const savedModel = localStorage.getItem('trader-copilot-model');
  if (savedModel && savedModel in MODELS) {
    useSystemStore.getState().setModelId(savedModel);
  }
  
  const savedWebSearch = localStorage.getItem('trader-copilot-websearch');
  if (savedWebSearch) {
    useSystemStore.getState().setEnableWebSearch(savedWebSearch === 'true');
  }
}

export { MODELS };