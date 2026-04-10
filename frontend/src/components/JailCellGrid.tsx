// frontend/src/components/JailCellGrid.tsx
/**
 * JailCellGrid - Jail cell visualization with country-based prisoners
 * Phase 2: Core Visualization, Phase 3: Animated Prisoners,
 * Phase 9: Country-based Attack Aggregation
 *
 * Displays up to 20 country prisoners in a stone-textured cell with iron bar overlay.
 * Countries sorted by attack count descending; least-attacked drop off via AnimatePresence exit.
 * Empty state shows "The cell is empty. Waiting for attackers..." with CRT effect.
 *
 * Per D-01: One slot per country (not per attack).
 * Per D-03: 20-country cap (least-attacked countries drop off).
 * Per D-08: FLIP animation via layout prop for smooth reordering.
 * Per D-10: Data derived on frontend from useCountryPrisoners hook.
 */

'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { useSocket } from '@/context/SocketContext';
import { useCountryPrisoners } from '@/hooks/useCountryPrisoners';
import { CountrySlot } from './CountrySlot';

export function JailCellGrid() {
  const { state } = useSocket();
  const countryPrisoners = useCountryPrisoners(state.attacks);

  return (
    <div className="relative h-full cell-texture rounded-lg overflow-hidden">
      {/* Iron bar overlay */}
      <div className="absolute inset-0 cell-bars" />

      {/* Empty state */}
      {countryPrisoners.length === 0 && (
        <div className="absolute inset-0 flex items-center justify-center crt-scanlines">
          <p className="font-mono text-text-muted text-center px-lg">
            The cell is empty.
            <br />
            Waiting for attackers...
          </p>
        </div>
      )}

      {/* Country prisoner grid - responsive auto-fill layout */}
      <div className="absolute inset-0 grid grid-cols-[repeat(auto-fill,minmax(3.5rem,1fr))] gap-sm p-md overflow-auto content-start">
        <AnimatePresence mode="popLayout">
          {countryPrisoners.map((country) => (
            <motion.div
              key={country.countryCode}
              layout
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.25, ease: 'easeOut' }}
            >
              <CountrySlot country={country} />
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}