// frontend/src/components/ArrestRecordTooltip.tsx
/**
 * ArrestRecordTooltip - Hover tooltip for attack details
 * Phase 3: Animated Prisoners
 *
 * Displays arrest record information with terminal aesthetic.
 * Per D-16: 150ms hover delay, positioned above avatar, terminal styling.
 * Per TOOL-01 through TOOL-03: Hover behavior and content display.
 */

import type { AttackEvent } from '@/types/attack';
import { countryCodeToFlag } from '@/utils/countryToFlag';
import { ARCHETYPE_LABELS, ARCHETYPE_COLORS } from '@/utils/archetypes';

/**
 * Convert ISO timestamp to relative time string
 */
function formatTimeAgo(timestamp: string): string {
  const now = new Date();
  const then = new Date(timestamp);
  const diffSeconds = Math.floor((now.getTime() - then.getTime()) / 1000);

  if (diffSeconds < 60) {
    return 'just now';
  }

  const diffMinutes = Math.floor(diffSeconds / 60);
  if (diffMinutes < 60) {
    return `${diffMinutes}m ago`;
  }

  const diffHours = Math.floor(diffMinutes / 60);
  if (diffHours < 24) {
    return `${diffHours}h ago`;
  }

  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays}d ago`;
}

/**
 * Convert duration in seconds to "Xm Xs" format
 */
function formatDuration(seconds: number): string {
  if (seconds < 60) {
    return `${seconds}s`;
  }

  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes}m ${remainingSeconds}s`;
}


interface ArrestRecordTooltipProps {
  attack: AttackEvent;
}

export function ArrestRecordTooltip({ attack }: ArrestRecordTooltipProps) {
  const archetypeLabel = ARCHETYPE_LABELS[attack.archetype] || attack.archetype.toUpperCase();
  const archetypeColor = ARCHETYPE_COLORS[attack.archetype] || '#00FF88';
  const flagEmoji = countryCodeToFlag(attack.countryCode);

  return (
    <div
      className={`
        absolute -top-2 left-1/2 -translate-x-1/2
        w-[280px]
        bg-[#1A1A1A]
        border border-[#00FF88]
        rounded-lg
        p-3
        font-mono text-sm
        z-50
      `}
      style={{ transform: 'translateX(-50%) translateY(-100%)' }}
    >
      {/* Archetype badge */}
      <div
        className="inline-block px-2 py-0.5 rounded text-xs uppercase mb-2"
        style={{
          backgroundColor: 'rgba(0, 255, 136, 0.15)',
          color: archetypeColor,
        }}
      >
        {archetypeLabel}
      </div>

      {/* Attack details */}
      <div className="space-y-1.5 text-xs">
        {/* IP address */}
        <div className="flex justify-between">
          <span className="text-[#6B6B6B]">IP</span>
          <span className="text-[#00FF88]">{attack.ip}</span>
        </div>

        {/* Country */}
        <div className="flex justify-between">
          <span className="text-[#6B6B6B]">Country</span>
          <span className="text-[#00FF88]">
            {flagEmoji} {attack.country}
          </span>
        </div>

        {/* Protocol/Port */}
        <div className="flex justify-between">
          <span className="text-[#6B6B6B]">Port</span>
          <span className="text-[#00FF88]">
            {attack.protocol}/{attack.port}
          </span>
        </div>

        {/* Commands count */}
        <div className="flex justify-between">
          <span className="text-[#6B6B6B]">Commands</span>
          <span className="text-[#00FF88]">{attack.commands.length}</span>
        </div>

        {/* Duration */}
        <div className="flex justify-between">
          <span className="text-[#6B6B6B]">Duration</span>
          <span className="text-[#00FF88]">{formatDuration(attack.duration)}</span>
        </div>

        {/* Time arrested */}
        <div className="flex justify-between">
          <span className="text-[#6B6B6B]">Arrested</span>
          <span className="text-[#00FF88]">{formatTimeAgo(attack.timestamp)}</span>
        </div>
      </div>
    </div>
  );
}