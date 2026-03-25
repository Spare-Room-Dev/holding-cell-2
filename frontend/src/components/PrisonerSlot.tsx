// frontend/src/components/PrisonerSlot.tsx
/**
 * PrisonerSlot - Animated prisoner slot with hover tooltip
 * Phase 3: Animated Prisoners
 *
 * Renders pixel-art prisoner sprites with spring entrance animation.
 * Per D-17: New prisoners enter from above with spring physics.
 * Per D-16: 150ms hover delay before tooltip shows.
 * Per TOOL-02/TOOL-03: Tooltip shows after hover delay, dismisses immediately on mouse leave.
 */

'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { AttackEvent } from '@/types/attack';
import { PrisonerSprite } from './PrisonerSprite';
import { ArrestRecordTooltip } from './ArrestRecordTooltip';

interface PrisonerSlotProps {
  attack: AttackEvent;
  isNew?: boolean; // true for newly added prisoners - triggers entrance animation
}

export function PrisonerSlot({ attack, isNew = false }: PrisonerSlotProps) {
  // Hover state management for tooltip (per D-16: 150ms delay)
  const [isHovered, setIsHovered] = useState(false);
  const [showTooltip, setShowTooltip] = useState(false);

  // 150ms hover delay before showing tooltip
  useEffect(() => {
    let timeoutId: NodeJS.Timeout;
    if (isHovered) {
      timeoutId = setTimeout(() => setShowTooltip(true), 150);
    }
    return () => clearTimeout(timeoutId);
  }, [isHovered]);

  return (
    <motion.div
      layout
      className="relative"
      initial={isNew ? { y: -100, opacity: 0 } : false}
      animate={{ y: 0, opacity: 1 }}
      transition={
        isNew
          ? { type: 'spring', stiffness: 300, damping: 20 }
          : { type: 'spring', stiffness: 400, damping: 25 }
      }
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => {
        setIsHovered(false);
        setShowTooltip(false);
      }}
    >
      <PrisonerSprite archetype={attack.archetype} />

      {/* Tooltip with entrance/exit animation */}
      <AnimatePresence>
        {showTooltip && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.15 }}
          >
            <ArrestRecordTooltip attack={attack} />
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}