// frontend/src/components/PrisonerSprite.tsx
/**
 * PrisonerSprite - Pixel-art prisoner sprites as inline SVG
 * Phase 3: Animated Prisoners, Phase 9: Country-based Attack Aggregation
 *
 * Renders a 32x32 pixel-art SVG scaled to display.
 * Bandana color matches archetype for visual identification.
 * When countryCode is provided, flag emoji replaces bandana as primary identifier.
 * Per D-02: Country flag replaces bandana color when countryCode is set.
 * Per D-14: Inline SVG sprites (no external image files).
 * Per D-15: Bandana colors match ARCHETYPE_COLORS mapping.
 */

import type { Archetype } from '@/types/attack';
import { countryCodeToFlag } from '@/utils/countryToFlag';

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
  countryCode?: string;
  className?: string;
}

export function PrisonerSprite({ archetype, countryCode, className }: PrisonerSpriteProps) {
  const bandanaColor = BANDANA_COLORS[archetype];
  const showFlag = !!countryCode;

  return (
    <div className={`w-14 h-14 flex flex-col items-center justify-center ${className || ''}`}>
      {/* Country flag above sprite (replaces bandana as primary identifier) */}
      {showFlag && (
        <span className="w-6 text-center inline-block text-base leading-none -mb-1">
          {countryCodeToFlag(countryCode!)}
        </span>
      )}
      <svg
        viewBox="0 0 32 32"
        width={showFlag ? 48 : 56}
        height={showFlag ? 48 : 56}
        style={{ imageRendering: 'pixelated' }}
        className="pixel-sprite"
        aria-label={showFlag ? `prisoner from ${countryCode}` : `${archetype.replace('_', ' ')} prisoner`}
      >
        {/* Bandana - gray when flag shown, archetype color otherwise */}
        <rect x="10" y="4" width="12" height="4" fill={showFlag ? '#444444' : bandanaColor} />

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