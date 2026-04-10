// frontend/src/components/CountrySlot.tsx
/**
 * CountrySlot - Per-country animated prisoner slot with hover tooltip
 * Phase 9: Country-based Attack Aggregation
 *
 * Renders a single country's prisoner slot with:
 * - Spring entrance animation when isNew is true (D-06)
 * - Phosphor green pulse glow on count update (D-07)
 * - Hover tooltip showing archetype breakdown (D-04, D-05)
 * - FLIP reordering via layout prop (D-08)
 *
 * Follows the PrisonerSlot pattern for hover behavior (150ms delay).
 * Per Pitfall 4: pulse does NOT trigger on initial render or first appearance.
 */

'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { CountryPrisoner, Archetype } from '@/types/attack';
import { PrisonerSprite } from './PrisonerSprite';
import { CountryTooltip } from './CountryTooltip';

interface CountrySlotProps {
  country: CountryPrisoner;
}

/**
 * Returns the archetype with the highest attack count for the given country.
 * Determines which sprite body to render (even though bandana is gray,
 * the archetype still provides visual variety).
 */
function getMostCommonArchetype(country: CountryPrisoner): Archetype {
  const entries = Object.entries(country.archetypes) as [Archetype, number][];
  if (entries.length === 0) {
    return 'botnet_drone'; // fallback
  }
  return entries.reduce((max, [arch, count]) =>
    count > max[1] ? [arch, count] : max
  , entries[0])[0] as Archetype;
}

export function CountrySlot({ country }: CountrySlotProps) {
  // Hover state management (150ms delay per D-05, same as PrisonerSlot)
  const [isHovered, setIsHovered] = useState(false);
  const [showTooltip, setShowTooltip] = useState(false);

  useEffect(() => {
    let timeoutId: NodeJS.Timeout;
    if (isHovered) {
      timeoutId = setTimeout(() => setShowTooltip(true), 150);
    }
    return () => clearTimeout(timeoutId);
  }, [isHovered]);

  // Determine the most common archetype for the sprite body
  const primaryArchetype = getMostCommonArchetype(country);

  // Pulse animation: phosphor green glow when isUpdated transitions to true (D-07)
  // Per Pitfall 4: only pulses when isUpdated is true (hook ensures false on first appearance)
  const pulseAnimation = country.isUpdated
    ? {
        boxShadow: [
          '0 0 0px rgba(0,255,136,0)',
          '0 0 12px rgba(0,255,136,0.4)',
          '0 0 0px rgba(0,255,136,0)',
        ],
      }
    : {};

  const pulseTransition = country.isUpdated ? { duration: 0.3 } : {};

  return (
    <motion.div
      layout
      className="relative"
      initial={country.isNew ? { y: -100, opacity: 0 } : false}
      animate={{ y: 0, opacity: 1 }}
      transition={
        country.isNew
          ? { type: 'spring', stiffness: 300, damping: 20 }
          : { type: 'spring', stiffness: 400, damping: 25 }
      }
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => {
        setIsHovered(false);
        setShowTooltip(false);
      }}
    >
      <motion.div animate={pulseAnimation} transition={pulseTransition}>
        <PrisonerSprite
          archetype={primaryArchetype}
          countryCode={country.countryCode}
        />
        <div className="text-[11px] text-[#00FF88] font-mono text-center mt-0.5">
          {country.count.toLocaleString()}
        </div>
      </motion.div>

      {/* Tooltip with entrance/exit animation */}
      <AnimatePresence>
        {showTooltip && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.15 }}
          >
            <CountryTooltip country={country} />
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}