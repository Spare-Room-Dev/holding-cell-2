// frontend/src/components/JailCellGrid.tsx
/**
 * JailCellGrid - Jail cell visualization with prisoners
 * Phase 2: Core Visualization
 *
 * Displays up to 20 prisoners in a stone-textured cell with iron bar overlay.
 * Prisoners stack from bottom, newest on top (LIFO order).
 * Empty state shows "The cell is empty. Waiting for attackers..." with CRT effect.
 *
 * Per D-04: CSS-only stone/brick texture (cell-texture class)
 * Per D-05: Iron bar overlay via CSS (cell-bars class)
 * Per D-07: Fixed 20-slot visual
 * Per D-08: Fade-out when count exceeds 20
 * Per D-09: LIFO order (newest at top)
 * Per D-13: Empty state with pixel font aesthetic
 * Per D-14: CRT scanline overlay on empty state
 */

'use client';

import { motion, AnimatePresence } from 'motion/react';
import { useSocket } from '@/context/SocketContext';
import { PrisonerSlot } from './PrisonerSlot';

export function JailCellGrid() {
  const { state } = useSocket();
  const attacks = state.attacks;

  // Show last 20 attacks, newest first (LIFO - per D-09)
  // Attacks array is already newest first from SocketContext
  const visibleAttacks = attacks.slice(0, 20);

  return (
    <div className="relative h-full cell-texture rounded-lg overflow-hidden">
      {/* Iron bar overlay (per D-05) */}
      <div className="absolute inset-0 cell-bars" />

      {/* Empty state (per D-13, D-14) */}
      {visibleAttacks.length === 0 && (
        <div className="absolute inset-0 flex items-center justify-center crt-scanlines">
          <p className="font-mono text-text-muted text-center px-lg">
            The cell is empty.
            <br />
            Waiting for attackers...
          </p>
        </div>
      )}

      {/* Prisoner stack - flex-col-reverse stacks from bottom (per D-03) */}
      <div className="absolute inset-0 flex flex-col-reverse gap-sm p-md overflow-hidden">
        <AnimatePresence mode="popLayout">
          {visibleAttacks.map((attack) => (
            <motion.div
              key={attack.id}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.25, ease: 'easeOut' }}
            >
              <PrisonerSlot attack={attack} />
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}