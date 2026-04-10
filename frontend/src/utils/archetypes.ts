/**
 * Shared archetype display constants.
 * Used by ArrestRecordTooltip, CountryTooltip, and useCountryPrisoners hook.
 * Per research: extracting prevents duplication across components.
 */

import type { Archetype } from '@/types/attack';

export const ARCHETYPE_LABELS: Record<Archetype, string> = {
  script_kiddie: 'SCRIPT KIDDIE',
  botnet_drone: 'BOTNET DRONE',
  apt_operative: 'APT OPERATIVE',
  iot_worm: 'IOT WORM',
  hacktivist: 'HACKTIVIST',
};

export const ARCHETYPE_COLORS: Record<Archetype, string> = {
  script_kiddie: '#FFB800',
  botnet_drone: '#00FF88',
  apt_operative: '#FF3B5C',
  iot_worm: '#A855F7',
  hacktivist: '#60A5FA',
};