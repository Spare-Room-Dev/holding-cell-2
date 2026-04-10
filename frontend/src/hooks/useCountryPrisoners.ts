/**
 * useCountryPrisoners - Aggregation hook for country-based attack visualization
 * Phase 9: Country-based Attack Aggregation
 *
 * Groups the flat attacks[] array by countryCode, computing attack counts,
 * archetype breakdowns, and tracking isNew/isUpdated flags for animation.
 *
 * Per D-03: 20-country cap enforced via slice(0, 20).
 * Per Pitfall 1 (RESEARCH): isNew uses useRef to compare previous/current country sets.
 * Per Pitfall 4 (RESEARCH): isUpdated requires prevCount > 0 to prevent pulse on first appearance.
 */

import { useMemo, useRef } from 'react';
import type { AttackEvent, Archetype, CountryPrisoner } from '@/types/attack';
import { getCountryName } from '@/utils/countryNames';

export function useCountryPrisoners(attacks: AttackEvent[]): CountryPrisoner[] {
  const prevCountrySetRef = useRef<Set<string>>(new Set());
  const prevCountsRef = useRef<Record<string, number>>({});

  const countryPrisoners = useMemo(() => {
    const countryMap = new Map<string, {
      countryCode: string;
      countryName: string;
      count: number;
      archetypes: Partial<Record<Archetype, number>>;
      lastAttack: string;
    }>();

    for (const attack of attacks) {
      const existing = countryMap.get(attack.countryCode);
      if (existing) {
        existing.count += 1;
        existing.archetypes[attack.archetype] =
          (existing.archetypes[attack.archetype] || 0) + 1;
        if (attack.timestamp > existing.lastAttack) {
          existing.lastAttack = attack.timestamp;
        }
      } else {
        countryMap.set(attack.countryCode, {
          countryCode: attack.countryCode,
          countryName: getCountryName(attack.countryCode),
          count: 1,
          archetypes: { [attack.archetype]: 1 },
          lastAttack: attack.timestamp,
        });
      }
    }

    const prevSet = prevCountrySetRef.current;
    const newSet = new Set(countryMap.keys());

    // Compute isNew and isUpdated before sorting/slicing
    const result = Array.from(countryMap.values()).map((cp) => ({
      ...cp,
      isNew: !prevSet.has(cp.countryCode),
      isUpdated: prevCountsRef.current[cp.countryCode] !== undefined
        && prevCountsRef.current[cp.countryCode] > 0
        && cp.count > prevCountsRef.current[cp.countryCode],
    }));

    // Sort by count descending
    result.sort((a, b) => b.count - a.count);

    // Apply 20-country cap per D-03
    const capped = result.slice(0, 20);

    // Update refs for next render:
    // - prevCountrySetRef tracks ALL countries seen (before slicing)
    // - prevCountsRef tracks counts for countries in the capped array
    prevCountrySetRef.current = newSet;
    prevCountsRef.current = {};
    for (const cp of capped) {
      prevCountsRef.current[cp.countryCode] = cp.count;
    }

    return capped;
  }, [attacks]);

  return countryPrisoners;
}