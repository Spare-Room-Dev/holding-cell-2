// frontend/src/components/PrisonerSprite.tsx
/**
 * PrisonerSprite - Pixel-art prisoner sprites as inline SVG
 * Phase 3: Animated Prisoners
 *
 * Renders a 32x32 pixel-art SVG scaled to 56x56 display.
 * Bandana color matches archetype for visual identification.
 * Per D-14: Inline SVG sprites (no external image files).
 * Per D-15: Bandana colors match ARCHETYPE_COLORS mapping.
 */

import type { Archetype } from '@/types/attack';

// Bandana colors mapping (hex values for direct SVG use)
const BANDANA_COLORS: Record<Archetype, string> = {
  script_kiddie: '#FFB800', // amber
  botnet_drone: '#00FF88', // phosphor
  apt_operative: '#FF3B5C', // alert
  iot_worm: '#A855F7', // purple-400
  hacktivist: '#60A5FA', // blue-400
};

interface PrisonerSpriteProps {
  archetype: Archetype;
  className?: string;
}

export function PrisonerSprite({ archetype, className }: PrisonerSpriteProps) {
  const bandanaColor = BANDANA_COLORS[archetype];

  return (
    <div className={`w-14 h-14 flex items-center justify-center ${className || ''}`}>
      <svg
        viewBox="0 0 32 32"
        width="56"
        height="56"
        style={{ imageRendering: 'pixelated' }}
        className="pixel-sprite"
        aria-label={`${archetype.replace('_', ' ')} prisoner`}
      >
        {/* Bandana - colored by archetype */}
        <rect x="10" y="4" width="12" height="4" fill={bandanaColor} />

        {/* Head - white/gray */}
        <rect x="10" y="6" width="12" height="10" fill="#F0F0F0" />

        {/* Eyes - black pixels */}
        <rect x="12" y="10" width="2" height="2" fill="#0D0D0D" />
        <rect x="18" y="10" width="2" height="2" fill="#0D0D0D" />

        {/* Body - white/gray */}
        <rect x="12" y="16" width="8" height="12" fill="#F0F0F0" />

        {/* Arms - darker shade */}
        <rect x="8" y="18" width="4" height="8" fill="#D0D0D0" />
        <rect x="20" y="18" width="4" height="8" fill="#D0D0D0" />

        {/* Legs - dark */}
        <rect x="12" y="28" width="4" height="4" fill="#1A1A1A" />
        <rect x="16" y="28" width="4" height="4" fill="#1A1A1A" />
      </svg>
    </div>
  );
}