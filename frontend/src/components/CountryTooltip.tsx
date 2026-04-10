// frontend/src/components/CountryTooltip.tsx
/**
 * CountryTooltip - Hover tooltip for country-based attack details
 * Phase 9: Country-based Attack Aggregation
 *
 * Displays country flag, country name, total attack count,
 * and archetype breakdown bars with proportional widths.
 * Per D-04: Tooltip shows archetype breakdown as colored horizontal bars.
 * Per D-05: Terminal aesthetic maintained (dark bg, phosphor green, monospace).
 */

import type { CountryPrisoner, Archetype } from '@/types/attack';
import { ARCHETYPE_LABELS, ARCHETYPE_COLORS } from '@/utils/archetypes';
import { countryCodeToFlag } from '@/utils/countryToFlag';

interface CountryTooltipProps {
  country: CountryPrisoner;
}

export function CountryTooltip({ country }: CountryTooltipProps) {
  const flagEmoji = countryCodeToFlag(country.countryCode);
  // Per RESEARCH Pattern 4: proportional bars where max archetype fills 100%
  const maxCount = Math.max(...(Object.values(country.archetypes) as number[]), 1);

  // Sort archetype entries by count descending for display
  const sortedArchetypes = (
    Object.entries(country.archetypes) as [Archetype, number][]
  ).sort(([, a], [, b]) => b - a);

  return (
    <div
      className="absolute -top-2 left-1/2 -translate-x-1/2 w-[260px] bg-[#1A1A1A] border border-[#00FF88] rounded-lg p-3 font-mono text-sm z-50"
      style={{ transform: 'translateX(-50%) translateY(-100%)' }}
    >
      {/* Country header: flag + name */}
      <div className="flex items-center gap-xs mb-2">
        <span className="w-6 text-center inline-block text-xl">{flagEmoji}</span>
        <span className="text-[#00FF88] text-xs uppercase">{country.countryName}</span>
      </div>

      {/* Total attacks row */}
      <div className="flex justify-between text-xs mb-2">
        <span className="text-[#6B6B6B]">TOTAL ATTACKS</span>
        <span className="text-[#00FF88]">{country.count.toLocaleString()}</span>
      </div>

      {/* Archetype breakdown bars */}
      <div className="space-y-1">
        {sortedArchetypes.map(([archetype, count]) => (
          <div key={archetype} className="flex items-center gap-xs">
            <span className="text-[10px] text-text-muted w-20 truncate">
              {ARCHETYPE_LABELS[archetype]}
            </span>
            <div className="flex-1 h-1.5 bg-[#0D0D0D] rounded-full overflow-hidden">
              <div
                className="h-full rounded-full"
                style={{
                  width: `${(count / maxCount) * 100}%`,
                  backgroundColor: ARCHETYPE_COLORS[archetype],
                }}
              />
            </div>
            <span className="text-[10px] text-[#00FF88] w-5 text-right">{count}</span>
          </div>
        ))}
      </div>
    </div>
  );
}