// frontend/src/components/PrisonerSlot.tsx
/**
 * PrisonerSlot - Archetype-colored prisoner placeholder
 * Phase 2: Core Visualization
 *
 * Renders a 56px square box colored by attacker archetype.
 * This is a placeholder for Phase 3 pixel-art sprites.
 * Per D-10: Archetype-colored boxes as placeholder sprites.
 * Per D-12: No hover tooltip in Phase 2.
 */

import type { AttackEvent, Archetype } from '@/types/attack';

// Archetype color mapping (per D-11: use existing ARCHETYPE_COLORS pattern)
const ARCHETYPE_COLORS: Record<Archetype, string> = {
  script_kiddie: 'amber',
  botnet_drone: 'phosphor',
  apt_operative: 'alert',
  iot_worm: 'purple-400',
  hacktivist: 'blue-400',
};

interface PrisonerSlotProps {
  attack: AttackEvent;
}

export function PrisonerSlot({ attack }: PrisonerSlotProps) {
  const colorKey = ARCHETYPE_COLORS[attack.archetype];

  return (
    <div
      className={`
        w-14 h-14
        bg-${colorKey}/20
        border-2 border-${colorKey}
        rounded-md
        flex items-center justify-center
      `}
    >
      {/* Phase 2: Placeholder - archetype initial */}
      <span className={`text-${colorKey} font-mono text-sm font-bold`}>
        {attack.archetype.charAt(0).toUpperCase()}
      </span>
    </div>
  );
}