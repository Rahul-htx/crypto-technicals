import fs from 'fs/promises';
import crypto from 'crypto';
import path from 'path';

interface Snapshot {
  meta: {
    last_updated: string;
    horizons_present: string[];
    coins_tracked: string[];
  };
  [horizon: string]: any;
}

interface CachedSnapshot {
  json: Snapshot | null;
  hash: string;
  loadedAt: number;
}

class KeyValueStore {
  private snapshot: CachedSnapshot = {
    json: null,
    hash: '',
    loadedAt: 0
  };

  private getSnapshotPath(): string {
    return path.join(process.cwd(), process.env.SNAPSHOT_PATH || '../data/runs/snapshots/latest_snapshot.json');
  }

  private sha256(content: string): string {
    return crypto.createHash('sha256').update(content).digest('hex').substring(0, 8);
  }

  async load(): Promise<CachedSnapshot> {
    try {
      const snapshotPath = this.getSnapshotPath();
      const file = await fs.readFile(snapshotPath, 'utf-8');
      const hash = this.sha256(file);
      
      // Only parse if hash changed
      if (hash !== this.snapshot.hash) {
        console.log(`Loading new snapshot with hash: ${hash}`);
        this.snapshot = {
          json: JSON.parse(file),
          hash,
          loadedAt: Date.now()
        };
      }
      
      return this.snapshot;
    } catch (error) {
      console.error('Failed to load snapshot:', error);
      return {
        json: null,
        hash: 'error',
        loadedAt: Date.now()
      };
    }
  }

  getCurrentHash(): string {
    return this.snapshot.hash;
  }

  getLastUpdated(): number {
    return this.snapshot.loadedAt;
  }
}

// Global singleton instance
export const kv = new KeyValueStore();
export type { Snapshot };