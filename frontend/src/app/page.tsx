// frontend/src/app/page.tsx
/**
 * Dashboard - Main holding cell visualization page
 * Phase 2: Core Visualization
 * Phase 4: Responsive layout (per D-01 through D-04)
 *
 * Layout:
 * - Desktop (>=1024px): 70/30 sidebar layout (per D-01)
 * - Tablet (768px-1023px): Stacked layout, stats below JailCellGrid
 * - Mobile (<768px): Stats hidden in sidebar, shown via bottom sheet
 */

'use client';

import { useState } from 'react';
import { ConnectionStatus } from '@/components/ConnectionStatus';
import { JailCellGrid } from '@/components/JailCellGrid';
import { StatsPanel } from '@/components/StatsPanel';
import { ThemeToggle } from '@/components/ThemeToggle';
import { BottomSheet } from '@/components/BottomSheet';

export default function Dashboard() {
  const [isStatsOpen, setIsStatsOpen] = useState(false);

  return (
    <main className="min-h-screen bg-background text-text-primary">
      {/* Header */}
      <header className="flex items-center justify-between px-lg py-md border-b border-border">
        <h1 className="font-display text-h1 text-text-primary">
          Holding Cell
        </h1>
        <div className="flex items-center gap-md">
          <ConnectionStatus />
          <ThemeToggle />
          {/* Mobile stats button - visible on mobile/tablet, hidden on desktop */}
          <button
            className="lg:hidden px-sm py-xs rounded-md bg-surface-raised border border-border hover:bg-surface transition-colors text-sm"
            onClick={() => setIsStatsOpen(true)}
            aria-label="Show statistics"
          >
            Stats
          </button>
        </div>
      </header>

      {/* Main content - responsive layout (per D-01 through D-04) */}
      <div className="p-lg h-[calc(100vh-5rem)]">
        {/* Desktop: flex-row 70/30, Tablet/Mobile: flex-col stacked */}
        <div className="flex flex-col lg:flex-row gap-md h-full">
          {/* Jail Cell - 70% on desktop, full width on mobile/tablet */}
          <div className="flex-[7] h-full min-h-[50vh] lg:min-h-0">
            <JailCellGrid />
          </div>
          {/* Stats Panel - 30% on desktop, hidden on mobile */}
          <div className="hidden lg:flex flex-[3] h-full overflow-y-auto bg-surface rounded-lg border border-border p-md">
            <StatsPanel />
          </div>
        </div>
      </div>

      {/* Mobile bottom sheet for stats (per D-05 through D-08) */}
      <BottomSheet isOpen={isStatsOpen} onClose={() => setIsStatsOpen(false)}>
        <StatsPanel />
      </BottomSheet>
    </main>
  );
}