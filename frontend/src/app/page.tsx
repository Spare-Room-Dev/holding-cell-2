// frontend/src/app/page.tsx
/**
 * Dashboard - Main holding cell visualization page
 * Phase 2: Core Visualization
 *
 * Layout: 70/30 sidebar split (per D-01)
 * - JailCellGrid: 70% width, full viewport height (per D-02)
 * - StatsPanel: 30% width, independent scroll (per D-03)
 */

'use client';

import { ConnectionStatus } from '@/components/ConnectionStatus';
import { JailCellGrid } from '@/components/JailCellGrid';
import { StatsPanel } from '@/components/StatsPanel';

export default function Dashboard() {
  return (
    <main className="min-h-screen bg-background text-text-primary">
      {/* Header */}
      <header className="flex items-center justify-between px-lg py-md border-b border-border">
        <h1 className="font-display text-h1 text-text-primary">
          Holding Cell
        </h1>
        <ConnectionStatus />
      </header>

      {/* Main content - 70/30 sidebar layout (per D-01, D-02, D-03) */}
      <div className="p-lg h-[calc(100vh-5rem)]">
        <div className="flex flex-row gap-md h-full">
          {/* Jail Cell - 70% width */}
          <div className="flex-[7] h-full">
            <JailCellGrid />
          </div>
          {/* Stats Panel - 30% width */}
          <div className="flex-[3] h-full overflow-y-auto bg-surface rounded-lg border border-border p-md">
            <StatsPanel />
          </div>
        </div>
      </div>
    </main>
  );
}